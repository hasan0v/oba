from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from app.database import get_db
from app.models.user import User
from app.utils.dependencies import get_current_user
import sys
import os

# Add ml directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ml'))

router = APIRouter()


# Pydantic schemas
class RecommendationRequest(BaseModel):
    user_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    limit: int = 10


class RecommendationResponse(BaseModel):
    product_id: str
    predicted_rating: float
    score: float


class SentimentRequest(BaseModel):
    text: str


class SentimentBatchRequest(BaseModel):
    texts: List[str]


class SentimentScores(BaseModel):
    positive: float
    neutral: float
    negative: float


class SentimentResponse(BaseModel):
    sentiment: str
    confidence: float
    scores: Optional[SentimentScores] = None


class SentimentQualityResponse(BaseModel):
    sentiment: str
    confidence: float
    scores: SentimentScores
    quality_score: float
    is_actionable: bool
    priority: str
    emoji: str


class ComplaintClassifyRequest(BaseModel):
    text: str


class ComplaintClassifyResponse(BaseModel):
    category: str
    priority: str
    confidence: float


class ForecastRequest(BaseModel):
    product_id: UUID
    days: int = 7


class ForecastResponse(BaseModel):
    date: str
    predicted_quantity: float
    lower_bound: float
    upper_bound: float


class StockoutRiskResponse(BaseModel):
    product_id: str
    stockout_risk: bool
    days_until_stockout: Optional[int]
    predicted_demand_7d: float
    current_stock: int
    recommendation: str


@router.post("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    request: RecommendationRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized product recommendations."""
    try:
        # Import recommendation engine
        from ml.recommendation_engine import RecommendationEngine
        
        engine = RecommendationEngine()
        
        # Try to load pre-trained model
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'models', 'recommendation_model.pkl')
        
        if os.path.exists(model_path):
            engine.load_model(model_path)
            
            user_id = str(request.user_id or current_user.id)
            recommendations = engine.get_recommendations(user_id, n=request.limit)
            
            return [
                RecommendationResponse(
                    product_id=rec['product_id'],
                    predicted_rating=rec['predicted_rating'],
                    score=rec['predicted_rating'] / 5.0
                )
                for rec in recommendations
            ]
        else:
            # Return empty if model not trained
            return []
            
    except Exception as e:
        # Log error and return empty recommendations
        print(f"Recommendation error: {e}")
        return []


@router.post("/sentiment", response_model=SentimentResponse)
async def analyze_sentiment(
    request: SentimentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment of Azerbaijani text using allmalab/bert-small-aze model.
    
    Returns sentiment classification (positive/neutral/negative) with confidence scores.
    """
    try:
        from ml.sentiment_analyzer import get_sentiment_analyzer
        
        analyzer = get_sentiment_analyzer()
        result = analyzer.analyze(request.text)
        
        return SentimentResponse(
            sentiment=result['sentiment'],
            confidence=result['confidence'],
            scores=SentimentScores(**result.get('scores', {})) if 'scores' in result else None
        )
    except Exception as e:
        # Simple fallback sentiment analysis
        text_lower = request.text.lower()
        
        positive_words = ['yaxşı', 'əla', 'gözəl', 'mükəmməl', 'super', 'bəyəndim', 'tövsiyə']
        negative_words = ['pis', 'xarab', 'köhnə', 'bəyənmədim', 'zəif', 'baha']
        
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count > negative_count:
            return SentimentResponse(sentiment='positive', confidence=0.7)
        elif negative_count > positive_count:
            return SentimentResponse(sentiment='negative', confidence=0.7)
        else:
            return SentimentResponse(sentiment='neutral', confidence=0.5)


@router.post("/sentiment/analyze", response_model=SentimentQualityResponse)
async def analyze_sentiment_quality(
    request: SentimentRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment with quality metrics for review prioritization.
    
    Returns:
    - sentiment: positive/neutral/negative
    - confidence: prediction confidence (0-1)
    - quality_score: overall review quality (0-1)
    - is_actionable: True if negative review needs attention
    - priority: high/medium/low
    - emoji: visual representation
    """
    try:
        from ml.sentiment_analyzer import get_sentiment_analyzer
        
        analyzer = get_sentiment_analyzer()
        result = analyzer.classify_review_quality(request.text)
        
        return SentimentQualityResponse(
            sentiment=result['sentiment'],
            confidence=result['confidence'],
            scores=SentimentScores(**result['scores']),
            quality_score=result['quality_score'],
            is_actionable=result['is_actionable'],
            priority=result['priority'],
            emoji=result['emoji']
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sentiment analysis failed: {str(e)}"
        )


@router.post("/sentiment/batch", response_model=List[SentimentResponse])
async def analyze_sentiment_batch(
    request: SentimentBatchRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Analyze sentiment for multiple texts in a single request.
    
    More efficient for bulk processing of reviews.
    """
    try:
        from ml.sentiment_analyzer import get_sentiment_analyzer
        
        analyzer = get_sentiment_analyzer()
        results = analyzer.analyze_batch(request.texts)
        
        return [
            SentimentResponse(
                sentiment=r['sentiment'],
                confidence=r['confidence'],
                scores=SentimentScores(**r.get('scores', {})) if 'scores' in r else None
            )
            for r in results
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Batch sentiment analysis failed: {str(e)}"
        )


@router.post("/classify-complaint", response_model=ComplaintClassifyResponse)
async def classify_complaint(
    request: ComplaintClassifyRequest,
    current_user: User = Depends(get_current_user)
):
    """Classify complaint category and priority."""
    try:
        from ml.complaint_classifier import ComplaintClassifier
        
        classifier = ComplaintClassifier()
        
        model_path = os.path.join(os.path.dirname(__file__), '..', '..', 'ml', 'models', 'complaint_classifier.pkl')
        
        if os.path.exists(model_path):
            classifier.load_model(model_path)
            result = classifier.classify(request.text)
            
            return ComplaintClassifyResponse(
                category=result['category'],
                priority=result['priority'],
                confidence=result['confidence']
            )
    except Exception as e:
        pass
    
    # Fallback classification based on keywords
    text_lower = request.text.lower()
    
    category_keywords = {
        'product': ['məhsul', 'süd', 'çörək', 'meyvə', 'xarab', 'köhnə', 'tarix'],
        'service': ['xidmət', 'işçi', 'kassir', 'növbə', 'gözləmə'],
        'delivery': ['çatdırılma', 'kuryer', 'gecikdi', 'ünvan'],
        'pricing': ['qiymət', 'endirim', 'baha', 'hesab', 'çek']
    }
    
    priority_keywords = {
        'high': ['xarab', 'zəhər', 'xəstə', 'çürük', 'qurd', 'təhlükə'],
        'medium': ['gecik', 'səhv', 'kobud', 'çirkli']
    }
    
    # Determine category
    category = 'other'
    max_matches = 0
    for cat, keywords in category_keywords.items():
        matches = sum(1 for kw in keywords if kw in text_lower)
        if matches > max_matches:
            max_matches = matches
            category = cat
    
    # Determine priority
    priority = 'low'
    for prio, keywords in priority_keywords.items():
        if any(kw in text_lower for kw in keywords):
            priority = prio
            break
    
    return ComplaintClassifyResponse(
        category=category,
        priority=priority,
        confidence=0.6
    )


@router.post("/forecast/{product_id}", response_model=List[ForecastResponse])
async def forecast_demand(
    product_id: UUID,
    days: int = 7,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Forecast product demand for next N days."""
    try:
        from ml.demand_forecaster import DemandForecaster
        
        forecaster = DemandForecaster()
        
        model_path = os.path.join(
            os.path.dirname(__file__), '..', '..', 'ml', 'models', 
            f'forecast_model_{product_id}.pkl'
        )
        
        if os.path.exists(model_path):
            forecaster.load_model(str(product_id), model_path)
            forecast_df = forecaster.forecast(str(product_id), periods=days)
            
            return [
                ForecastResponse(
                    date=row['date'].strftime('%Y-%m-%d'),
                    predicted_quantity=round(row['predicted_quantity'], 1),
                    lower_bound=round(row['lower_bound'], 1),
                    upper_bound=round(row['upper_bound'], 1)
                )
                for _, row in forecast_df.iterrows()
            ]
    except Exception as e:
        print(f"Forecast error: {e}")
    
    # Return mock forecast if model not available
    from datetime import datetime, timedelta
    import random
    
    forecasts = []
    base_quantity = random.randint(50, 150)
    
    for i in range(days):
        date = datetime.now() + timedelta(days=i+1)
        quantity = base_quantity + random.randint(-20, 20)
        
        # Weekend spike
        if date.weekday() >= 5:
            quantity = int(quantity * 1.3)
        
        forecasts.append(ForecastResponse(
            date=date.strftime('%Y-%m-%d'),
            predicted_quantity=quantity,
            lower_bound=quantity * 0.8,
            upper_bound=quantity * 1.2
        ))
    
    return forecasts


@router.get("/stockout-risk/{product_id}", response_model=StockoutRiskResponse)
async def check_stockout_risk(
    product_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check stockout risk for a product."""
    from app.models.product import Product
    
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Get forecast
    forecasts = await forecast_demand(product_id, days=7, current_user=current_user, db=db)
    
    total_demand = sum(f.predicted_quantity for f in forecasts)
    current_stock = product.stock_quantity
    
    stockout_risk = total_demand > current_stock
    days_until_stockout = None
    
    if stockout_risk:
        cumsum = 0
        for i, f in enumerate(forecasts):
            cumsum += f.predicted_quantity
            if cumsum > current_stock:
                days_until_stockout = i + 1
                break
    
    recommendation = "Stock sufficient"
    if stockout_risk:
        needed = int(total_demand - current_stock)
        recommendation = f"Order at least {needed} units to avoid stockout"
    
    return StockoutRiskResponse(
        product_id=str(product_id),
        stockout_risk=stockout_risk,
        days_until_stockout=days_until_stockout,
        predicted_demand_7d=round(total_demand, 1),
        current_stock=current_stock,
        recommendation=recommendation
    )
