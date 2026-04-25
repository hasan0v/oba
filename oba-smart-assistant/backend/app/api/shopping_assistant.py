"""
Gemini AI Shopping Assistant API
Conversational shopping with voice/text support
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from typing import List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field
import google.generativeai as genai  # type: ignore
from google.generativeai.types import GenerationConfig  # type: ignore
import json
import re

from app.database import get_db
from app.models.product import Product, Category
from app.models.cart import Cart, CartItem
from app.models.user import User
from app.utils.dependencies import get_current_user
from app.config import settings

router = APIRouter()

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)  # type: ignore

# Pydantic schemas for structured output
class ShoppingItem(BaseModel):
    product_name: str = Field(description="Name of the product user wants")
    quantity: int = Field(default=1, description="Quantity requested")
    unit: Optional[str] = Field(default=None, description="Unit like kg, piece, litr")

class ShoppingList(BaseModel):
    items: List[ShoppingItem] = Field(default_factory=list)
    is_complete: bool = Field(default=False, description="Whether user finished shopping")
    user_message: Optional[str] = Field(default=None, description="What user said")

class MatchedProduct(BaseModel):
    product_id: str
    product_name: str
    price: float
    discount_price: Optional[float]
    quantity: int
    unit: str
    in_stock: bool
    image_url: Optional[str]

class AssistantResponse(BaseModel):
    message: str  # Gemini's response text
    shopping_list: List[ShoppingItem]  # Current shopping list
    matched_products: List[MatchedProduct]  # Products found in database
    is_complete: bool  # Whether conversation is finished
    action: str  # "continue", "confirm", "add_to_cart", "error"

class ChatRequest(BaseModel):
    message: str  # User's text message (from speech-to-text)
    conversation_history: List[dict] = Field(default_factory=list)  # Previous messages
    current_shopping_list: List[ShoppingItem] = Field(default_factory=list)

# System prompt for Gemini
SYSTEM_PROMPT = """Sən OBA supermarketinin alış-veriş köməkçisisən. Azərbaycan dilində danış.

SƏNİN VƏZİFƏN:
1. İstifadəçini salamla və nə almaq istədiklərini soruş
2. İstifadəçinin dediklərini dinlə və alış-veriş siyahısına əlavə et
3. Hər məhsul üçün miqdarı da qeyd et (əgər deməyiblərsə 1 götür)
4. İstifadəçi "bitdi", "tamam", "bəsdir" deyənə qədər davam et
5. Sonda bütün siyahını oxu və təsdiq istə

QAYDALAR:
- Qısa və aydın cavab ver (1-2 cümlə)
- Hər dəfə "Başqa nə əlavə edək?" kimi sual ver
- İstifadəçi fikrini dəyişsə (məs. "alma istəmirəm") siyahıdan sil
- Miqdar dəyişdirmək istəsə dəyişdir
- Əgər anlaşılmaz bir şey desələr, yenidən soruş

NÜMUNƏ SÖHBƏTİ:
İstifadəçi: "salam"
Sən: "Salam! OBA-ya xoş gəlmisiniz! Bu gün nə almaq istəyirsiniz?"

İstifadəçi: "2 kilo alma, 1 litr süd"
Sən: "Əla! 2 kq alma və 1 litr süd əlavə etdim. Başqa nə əlavə edək?"

İstifadəçi: "bitdi"
Sən: "Yaxşı! Siyahınızda: 2 kq alma, 1 litr süd. Səbətə əlavə edim?"

ÖNƏMLİ: Cavabını YALNIZ JSON formatında ver. Heç bir əlavə mətn, izahat və ya markdown işarəsi (```) əlavə etmə. Yalnız JSON obyekti qaytar:

{"message": "İstifadəçiyə mesajın burda", "items": [{"product_name": "məhsul", "quantity": 1, "unit": "kg"}], "is_complete": false, "action": "continue"}

action dəyərləri:
- "continue": söhbət davam edir
- "confirm": istifadəçi bitirdi, təsdiq gözlə
- "add_to_cart": istifadəçi təsdiq etdi, səbətə əlavə et
- "cancel": istifadəçi ləğv etdi
"""


def search_products_by_name(db: Session, search_terms: List[str]) -> dict:
    """Search products by name and return matches"""
    results = {}
    
    for term in search_terms:
        # Clean up the term
        term = term.lower().strip()
        if not term:
            continue
            
        # Search in product names (Azerbaijani and English)
        search_pattern = f"%{term}%"
        products = db.query(Product).filter(
            Product.is_active == True,
            or_(
                func.lower(Product.name).like(search_pattern),
                func.lower(Product.name_en).like(search_pattern),
                func.lower(Product.brand).like(search_pattern)
            )
        ).limit(5).all()
        
        if products:
            results[term] = products
    
    return results


def get_or_create_cart(user_id: Any, db: Session) -> Cart:
    """Get user's cart or create one"""
    cart = db.query(Cart).filter(Cart.user_id == user_id).first()
    if not cart:
        cart = Cart(user_id=user_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)
    return cart


@router.post("/chat", response_model=AssistantResponse)
async def chat_with_assistant(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Chat with AI shopping assistant.
    Send user's message (from speech-to-text) and get AI response.
    """
    try:
        # Initialize Gemini model - using Gemini 2.0 Flash
        model = genai.GenerativeModel(  # type: ignore
            model_name="gemini-2.5-flash",
            generation_config=GenerationConfig(
                temperature=0.7,
                top_p=0.95,
                top_k=40,
                max_output_tokens=1024,
                response_mime_type="application/json",  # Force JSON output
            )
        )
        
        # Build conversation context
        conversation_context = f"""Sistem: {SYSTEM_PROMPT}

İstifadəçinin adı: {current_user.full_name or current_user.phone_number}

"""
        
        # Add conversation history
        if request.conversation_history:
            conversation_context += "Əvvəlki söhbət:\n"
            for msg in request.conversation_history[-10:]:  # Last 10 messages
                role = "İstifadəçi" if msg.get("role") == "user" else "Köməkçi"
                conversation_context += f"{role}: {msg.get('content', '')}\n"
        
        # Add current shopping list context
        if request.current_shopping_list:
            items_text = ", ".join([
                f"{item.quantity} {item.unit or 'ədəd'} {item.product_name}" 
                for item in request.current_shopping_list
            ])
            conversation_context += f"\nHazırkı siyahı: {items_text}\n"
        
        # Add user's new message
        conversation_context += f"\nİstifadəçi: {request.message}\n\nKöməkçi (JSON formatında cavab ver):"
        
        # Get Gemini response
        response = model.generate_content(conversation_context)
        response_text = response.text.strip()
        
        print(f"Gemini raw response: {response_text[:500]}")  # Debug log
        
        # Parse JSON from response
        ai_message = response_text
        items_data = []
        is_complete = False
        action = "continue"
        
        # Try to extract JSON from response - handle markdown code blocks
        # Remove markdown code block markers if present
        clean_response = response_text
        if "```json" in clean_response:
            clean_response = clean_response.replace("```json", "").replace("```", "").strip()
        elif "```" in clean_response:
            clean_response = clean_response.replace("```", "").strip()
        
        # Try to find JSON object
        json_match = re.search(r'\{[\s\S]*\}', clean_response)
        if json_match:
            try:
                parsed = json.loads(json_match.group())
                ai_message = parsed.get("message", "")
                items_data = parsed.get("items", [])
                is_complete = parsed.get("is_complete", False)
                action = parsed.get("action", "continue")
                print(f"Parsed message: {ai_message}")  # Debug log
            except json.JSONDecodeError as je:
                print(f"JSON parse error: {je}")
                # If JSON parsing fails, use the raw text but clean it up
                ai_message = response_text
                # Try to remove any JSON-like content from the message
                if "{" in ai_message:
                    ai_message = ai_message.split("{")[0].strip()
                if not ai_message:
                    ai_message = "Bağışlayın, anlamadım. Bir daha deyə bilərsiniz?"
        else:
            # No JSON found, use raw text
            ai_message = response_text
        
        # Ensure we have a valid message
        if not ai_message or ai_message.strip() == "":
            ai_message = "Bağışlayın, texniki problem var. Bir daha yoxlayın."
        
        # Convert items to ShoppingItem objects
        shopping_list = []
        for item in items_data:
            shopping_list.append(ShoppingItem(
                product_name=item.get("product_name", ""),
                quantity=item.get("quantity", 1),
                unit=item.get("unit")
            ))
        
        # Search for matching products in database
        search_terms = [item.product_name for item in shopping_list]
        product_matches = search_products_by_name(db, search_terms)
        
        # Build matched products list
        matched_products = []
        for item in shopping_list:
            term = item.product_name.lower().strip()
            if term in product_matches and product_matches[term]:
                product = product_matches[term][0]  # Best match
                matched_products.append(MatchedProduct(
                    product_id=str(product.id),
                    product_name=product.name,
                    price=product.price,
                    discount_price=product.discount_price,
                    quantity=item.quantity,
                    unit=item.unit or product.unit,
                    in_stock=product.stock_quantity > 0,
                    image_url=product.image_urls[0] if product.image_urls else None
                ))
        
        return AssistantResponse(
            message=ai_message,
            shopping_list=shopping_list,
            matched_products=matched_products,
            is_complete=is_complete,
            action=action
        )
        
    except Exception as e:
        print(f"Gemini API error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"AI assistant error: {str(e)}"
        )


@router.post("/add-to-cart")
async def add_shopping_list_to_cart(
    items: List[MatchedProduct],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add matched products from shopping assistant to cart.
    """
    try:
        cart = get_or_create_cart(current_user.id, db)
        added_items = []
        
        for item in items:
            # Get product from database
            product = db.query(Product).filter(
                Product.id == item.product_id,
                Product.is_active == True
            ).first()
            
            if not product:
                continue
            
            # Check if already in cart
            existing_item = db.query(CartItem).filter(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product.id
            ).first()
            
            if existing_item:
                # Update quantity
                existing_item.quantity = int(existing_item.quantity) + item.quantity  # type: ignore
            else:
                # Add new item
                cart_item = CartItem(
                    cart_id=cart.id,
                    product_id=product.id,
                    quantity=item.quantity
                )
                db.add(cart_item)
            
            added_items.append({
                "product_name": product.name,
                "quantity": item.quantity
            })
        
        db.commit()
        
        return {
            "success": True,
            "message": f"{len(added_items)} məhsul səbətə əlavə edildi",
            "added_items": added_items
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/start")
async def start_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Start a new shopping conversation.
    Returns initial greeting from assistant.
    """
    full_name = getattr(current_user, 'full_name', None)
    user_name = str(full_name) if full_name and str(full_name) != "None" else "Dost"
    first_name = user_name.split()[0] if user_name else "Dost"
    
    return AssistantResponse(
        message=f"Salam {first_name}! 🛒 OBA-ya xoş gəlmisiniz! Bu gün nə almaq istəyirsiniz?",
        shopping_list=[],
        matched_products=[],
        is_complete=False,
        action="continue"
    )


@router.get("/products/search")
async def search_products_for_assistant(
    query: str,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """
    Search products by name for assistant suggestions.
    """
    search_pattern = f"%{query.lower()}%"
    products = db.query(Product).filter(
        Product.is_active == True,
        or_(
            func.lower(Product.name).like(search_pattern),
            func.lower(Product.name_en).like(search_pattern),
            func.lower(Product.brand).like(search_pattern)
        )
    ).limit(limit).all()
    
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "price": p.price,
            "discount_price": p.discount_price,
            "unit": p.unit,
            "in_stock": p.stock_quantity > 0,
            "image_url": p.image_urls[0] if p.image_urls and len(p.image_urls) > 0 else None  # type: ignore
        }
        for p in products
    ]


# ============ Google Cloud Text-to-Speech ============
from google.cloud import texttospeech
from fastapi.responses import Response
import os
import base64

# Set credentials path
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
    "firebase-service-account.json"
)


class TTSRequest(BaseModel):
    text: str
    language_code: str = "tr-TR"  # Turkish as default (close to Azerbaijani)
    voice_name: Optional[str] = None  # e.g., "tr-TR-Wavenet-E" for female
    speaking_rate: float = 1.0
    pitch: float = 0.0


@router.post("/tts")
async def text_to_speech(request: TTSRequest):
    """
    Convert text to high-quality speech using Google Cloud TTS.
    Returns MP3 audio as base64 encoded string.
    
    Available voices for Turkish (tr-TR):
    - tr-TR-Standard-A to E (Standard voices)
    - tr-TR-Wavenet-A to E (Neural WaveNet - higher quality)
    
    For Azerbaijani-like sound, use Turkish female voice: tr-TR-Wavenet-E
    """
    try:
        client = texttospeech.TextToSpeechClient()
        
        # Set input text
        synthesis_input = texttospeech.SynthesisInput(text=request.text)
        
        # Select voice
        if request.voice_name:
            voice = texttospeech.VoiceSelectionParams(
                language_code=request.language_code,
                name=request.voice_name
            )
        else:
            # Default to WaveNet female voice for Turkish
            voice = texttospeech.VoiceSelectionParams(
                language_code=request.language_code,
                name="tr-TR-Wavenet-E",  # Female WaveNet voice
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
            )
        
        # Configure audio
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3,
            speaking_rate=request.speaking_rate,
            pitch=request.pitch
        )
        
        # Generate speech
        response = client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        # Return audio as base64
        audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
        
        return {
            "audio_content": audio_base64,
            "audio_format": "mp3",
            "text": request.text,
            "language": request.language_code
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"TTS Error: {str(e)}"
        )


@router.get("/tts/voices")
async def list_voices(language_code: str = "tr-TR"):
    """List available voices for a language."""
    try:
        client = texttospeech.TextToSpeechClient()
        response = client.list_voices(language_code=language_code)
        
        voices = []
        for voice in response.voices:
            voices.append({
                "name": voice.name,
                "language_codes": list(voice.language_codes),
                "gender": texttospeech.SsmlVoiceGender(voice.ssml_gender).name,
                "natural_sample_rate": voice.natural_sample_rate_hertz
            })
        
        return {"voices": voices, "language_code": language_code}
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing voices: {str(e)}"
        )
