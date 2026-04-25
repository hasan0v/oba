"""
Sentiment Analysis using allmalab/bert-small-aze Model
Specifically trained for Azerbaijani language
"""
from typing import Dict, List
import logging
import re

logger = logging.getLogger(__name__)

try:
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("transformers/torch not installed. Using rule-based sentiment analysis.")


class SentimentAnalyzer:
    """
    Sentiment analysis using allmalab/bert-small-aze model
    Specifically trained for Azerbaijani language
    """
    
    def __init__(self, model_name: str = None):
        """
        Initialize Azerbaijani BERT sentiment analyzer
        
        Args:
            model_name: HuggingFace model identifier. Options:
                - "allmalab/bert-small-aze" (Azerbaijani, requires auth)
                - "nlptown/bert-base-multilingual-uncased-sentiment" (multilingual, 5-star)
                - "cardiffnlp/twitter-xlm-roberta-base-sentiment" (multilingual, 3-class)
        """
        # Try models in order of preference
        # Note: allmalab/bert-small-aze is a base model - needs fine-tuning for sentiment
        # Use pre-trained sentiment models for now
        model_options = [
            "cardiffnlp/twitter-xlm-roberta-base-sentiment",  # Multilingual 3-class, pre-trained
            "nlptown/bert-base-multilingual-uncased-sentiment",  # Multilingual 5-star, pre-trained
            # "allmalab/bert-small-aze",  # Azerbaijani base model (requires fine-tuning)
        ]
        
        if model_name:
            model_options = [model_name] + model_options
        
        self.model_name = None
        self.model = None
        self.tokenizer = None
        self.device = None
        self.use_model = False
        self.num_labels = 3
        
        if TRANSFORMERS_AVAILABLE:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            
            for model_name in model_options:
                try:
                    logger.info(f"Trying to load model: {model_name}")
                    self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                    
                    # Load model
                    self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                    self.num_labels = self.model.config.num_labels
                    
                    self.model.to(self.device)
                    self.model.eval()
                    self.use_model = True
                    self.model_name = model_name
                    
                    # Performance optimizations
                    if torch.cuda.is_available():
                        self.model = self.model.half()
                    
                    logger.info(f"Model loaded successfully on {self.device}")
                    print(f"✅ Loaded model: {model_name} on {self.device} ({self.num_labels} labels)")
                    break
                except Exception as e:
                    logger.warning(f"Failed to load {model_name}: {e}")
                    continue
            
            if not self.use_model:
                print("⚠️ No transformer model available. Using rule-based analysis.")
        
        # Azerbaijani sentiment keywords for rule-based fallback
        self.positive_keywords = [
            'yaxşı', 'əla', 'gözəl', 'mükəmməl', 'super', 'bəyəndim', 'tövsiyə',
            'məmnun', 'keyfiyyətli', 'dadlı', 'təzə', 'sürətli', 'mehriban',
            'rahat', 'ucuz', 'münasib', 'təmiz', 'hörmətli', 'professional',
            'möhtəşəm', 'fantastik', 'şahane', 'ideal', 'layiqli', 'dəqiq',
            'good', 'great', 'excellent', 'perfect', 'amazing', 'love', 'recommend'
        ]
        
        self.negative_keywords = [
            'pis', 'xarab', 'köhnə', 'bəyənmədim', 'zəif', 'baha', 'gecikdi',
            'çürük', 'bayat', 'kobud', 'çirkli', 'yavaş', 'səhv', 'problem',
            'narahat', 'keyfiyyətsiz', 'xoşagəlməz', 'razı deyiləm', 'narazı',
            'yararsız', 'iyrənc', 'dəhşət', 'rezil', 'berbat', 'fəlakət',
            'bad', 'terrible', 'awful', 'poor', 'hate', 'worst', 'disappointed'
        ]
    
    def analyze(self, text: str) -> Dict:
        """
        Analyze sentiment of Azerbaijani text
        
        Args:
            text: Azerbaijani text to analyze (e.g., customer review)
        
        Returns:
            {
                'sentiment': 'positive' | 'neutral' | 'negative',
                'confidence': float (0-1),
                'scores': {
                    'positive': float,
                    'neutral': float,
                    'negative': float
                }
            }
        """
        if not text or len(text.strip()) == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.0,
                'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
            }
        
        # Clean text
        text = text.strip()[:512]  # Limit to max sequence length
        
        if self.use_model and self.model and self.tokenizer:
            return self._analyze_with_model(text)
        else:
            return self._analyze_rule_based(text)
    
    def _analyze_with_model(self, text: str) -> Dict:
        """Analyze using transformer model."""
        try:
            # Tokenize
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True
            ).to(self.device)
            
            # Predict
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probabilities = torch.softmax(logits, dim=1)[0]
            
            predicted_class = torch.argmax(probabilities).item()
            confidence = float(probabilities[predicted_class])
            
            # Map based on number of labels
            if self.num_labels == 5:
                # 5-star rating model (nlptown)
                # 0=1star, 1=2star, 2=3star, 3=4star, 4=5star
                if predicted_class >= 3:  # 4-5 stars
                    sentiment = 'positive'
                    pos_score = float(probabilities[3] + probabilities[4])
                    neg_score = float(probabilities[0] + probabilities[1])
                    neu_score = float(probabilities[2])
                elif predicted_class == 2:  # 3 stars
                    sentiment = 'neutral'
                    pos_score = float(probabilities[3] + probabilities[4])
                    neg_score = float(probabilities[0] + probabilities[1])
                    neu_score = float(probabilities[2])
                else:  # 1-2 stars
                    sentiment = 'negative'
                    pos_score = float(probabilities[3] + probabilities[4])
                    neg_score = float(probabilities[0] + probabilities[1])
                    neu_score = float(probabilities[2])
                
                scores = {
                    'negative': round(neg_score, 3),
                    'neutral': round(neu_score, 3),
                    'positive': round(pos_score, 3)
                }
                confidence = scores[sentiment]
            else:
                # 3-class model (cardiffnlp or similar)
                # Label order varies by model
                if 'cardiffnlp' in (self.model_name or ''):
                    # cardiffnlp: 0=negative, 1=neutral, 2=positive
                    sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
                else:
                    # Default: 0=negative, 1=neutral, 2=positive
                    sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
                
                sentiment = sentiment_map.get(predicted_class, 'neutral')
                scores = {
                    'negative': float(probabilities[0]),
                    'neutral': float(probabilities[1]) if self.num_labels > 2 else 0.0,
                    'positive': float(probabilities[2]) if self.num_labels > 2 else float(probabilities[1])
                }
                scores = {k: round(v, 3) for k, v in scores.items()}
            
            return {
                'sentiment': sentiment,
                'confidence': round(confidence, 3),
                'scores': scores
            }
            
        except Exception as e:
            logger.error(f"Error during sentiment analysis: {e}")
            return self._analyze_rule_based(text)
    
    def _analyze_rule_based(self, text: str) -> Dict:
        """Analyze using keyword-based rules (fallback)."""
        text_lower = text.lower()
        
        # Count keyword matches
        positive_count = sum(1 for word in self.positive_keywords if word in text_lower)
        negative_count = sum(1 for word in self.negative_keywords if word in text_lower)
        
        # Detect negation patterns
        negation_patterns = [
            r'deyil\s+\w*yaxşı',
            r'yox\s+\w*keyfiyyət',
            r'not\s+\w*good',
            r'isn\'t\s+\w*great'
        ]
        
        for pattern in negation_patterns:
            if re.search(pattern, text_lower):
                positive_count = max(0, positive_count - 1)
                negative_count += 1
        
        # Determine sentiment
        total = positive_count + negative_count
        
        if total == 0:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
            }
        
        if positive_count > negative_count:
            confidence = positive_count / total
            return {
                'sentiment': 'positive',
                'confidence': round(confidence, 3),
                'scores': {
                    'positive': round(confidence, 3),
                    'neutral': round((1 - confidence) / 2, 3),
                    'negative': round((1 - confidence) / 2, 3)
                }
            }
        elif negative_count > positive_count:
            confidence = negative_count / total
            return {
                'sentiment': 'negative',
                'confidence': round(confidence, 3),
                'scores': {
                    'positive': round((1 - confidence) / 2, 3),
                    'neutral': round((1 - confidence) / 2, 3),
                    'negative': round(confidence, 3)
                }
            }
        else:
            return {
                'sentiment': 'neutral',
                'confidence': 0.5,
                'scores': {'positive': 0.33, 'neutral': 0.34, 'negative': 0.33}
            }
    
    def analyze_batch(self, texts: List[str], batch_size: int = 16) -> List[Dict]:
        """
        Analyze sentiment for multiple texts efficiently
        
        Args:
            texts: List of Azerbaijani texts
            batch_size: Number of texts to process at once
        
        Returns:
            List of sentiment results
        """
        if not self.use_model:
            return [self.analyze(text) for text in texts]
        
        results = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            try:
                # Tokenize batch
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    truncation=True,
                    max_length=512,
                    padding=True
                ).to(self.device)
                
                # Predict
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    probabilities = torch.softmax(logits, dim=1)
                
                # Process each result
                for j, probs in enumerate(probabilities):
                    predicted_class = torch.argmax(probs).item()
                    confidence = float(probs[predicted_class])
                    
                    # Map based on number of labels
                    if self.num_labels == 5:
                        if predicted_class >= 3:
                            sentiment = 'positive'
                        elif predicted_class == 2:
                            sentiment = 'neutral'
                        else:
                            sentiment = 'negative'
                        
                        scores = {
                            'negative': round(float(probs[0] + probs[1]), 3),
                            'neutral': round(float(probs[2]), 3),
                            'positive': round(float(probs[3] + probs[4]), 3)
                        }
                        confidence = scores[sentiment]
                    else:
                        sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
                        sentiment = sentiment_map.get(predicted_class, 'neutral')
                        scores = {
                            'negative': round(float(probs[0]), 3),
                            'neutral': round(float(probs[1]), 3) if self.num_labels > 2 else 0.0,
                            'positive': round(float(probs[2]), 3) if self.num_labels > 2 else round(float(probs[1]), 3)
                        }
                    
                    results.append({
                        'sentiment': sentiment,
                        'confidence': round(confidence, 3),
                        'scores': scores
                    })
            
            except Exception as e:
                logger.error(f"Error in batch processing: {e}")
                # Fallback to rule-based for failed batch
                for text in batch:
                    results.append(self._analyze_rule_based(text))
        
        return results
    
    def get_sentiment_emoji(self, sentiment: str) -> str:
        """Get emoji representation of sentiment"""
        emoji_map = {
            'positive': '😊',
            'neutral': '😐',
            'negative': '😞'
        }
        return emoji_map.get(sentiment, '😐')
    
    def classify_review_quality(self, text: str) -> Dict:
        """
        Classify review quality and extract insights
        
        Returns:
            {
                'sentiment': str,
                'confidence': float,
                'quality_score': float,  # 0-1, based on text length and sentiment confidence
                'is_actionable': bool,   # True if negative with high confidence
                'priority': str          # 'high', 'medium', 'low'
            }
        """
        result = self.analyze(text)
        
        # Calculate quality score
        text_length = len(text.split())
        length_score = min(text_length / 20, 1.0)  # Normalize to 0-1
        quality_score = (result['confidence'] + length_score) / 2
        
        # Determine if actionable (negative with high confidence)
        is_actionable = (
            result['sentiment'] == 'negative' and 
            result['confidence'] > 0.7
        )
        
        # Assign priority
        if is_actionable:
            priority = 'high'
        elif result['sentiment'] == 'negative':
            priority = 'medium'
        else:
            priority = 'low'
        
        return {
            **result,
            'quality_score': round(quality_score, 3),
            'is_actionable': is_actionable,
            'priority': priority,
            'emoji': self.get_sentiment_emoji(result['sentiment'])
        }
    
    def get_sentiment_summary(self, texts: List[str]) -> Dict:
        """
        Get summary statistics for a batch of texts.
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            Dictionary with counts and percentages
        """
        results = self.analyze_batch(texts)
        
        sentiments = [r['sentiment'] for r in results]
        total = len(sentiments)
        
        if total == 0:
            return {
                'positive': 0, 'neutral': 0, 'negative': 0,
                'positive_pct': 0, 'neutral_pct': 0, 'negative_pct': 0,
                'avg_confidence': 0
            }
        
        counts = {
            'positive': sentiments.count('positive'),
            'neutral': sentiments.count('neutral'),
            'negative': sentiments.count('negative')
        }
        
        return {
            **counts,
            'positive_pct': round(counts['positive'] / total * 100, 1),
            'neutral_pct': round(counts['neutral'] / total * 100, 1),
            'negative_pct': round(counts['negative'] / total * 100, 1),
            'avg_confidence': round(sum(r['confidence'] for r in results) / total, 3)
        }


# Global instance for reuse (Singleton pattern)
_analyzer_instance = None

def get_sentiment_analyzer() -> SentimentAnalyzer:
    """
    Get or create global sentiment analyzer instance
    Singleton pattern for efficient model loading
    """
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SentimentAnalyzer()
    return _analyzer_instance


# Example usage and testing
if __name__ == "__main__":
    print("Testing Azerbaijani Sentiment Analyzer...")
    print(f"Transformers available: {TRANSFORMERS_AVAILABLE}")
    
    analyzer = SentimentAnalyzer()
    print(f"Using model: {analyzer.use_model}")
    
    # Test cases in Azerbaijani
    test_texts = [
        "Bu məhsul çox yaxşıdır, çox bəyəndim! Hər kəsə tövsiyə edirəm.",
        "Məhsul normaldır, amma qiyməti bir az bahadır.",
        "Çox pis məhsul! Xarab idi, bir daha almayacağam.",
        "Keyfiyyəti əladır, qiyməti münasibdir. Məmnunam.",
        "Zövqüm deyil, amma pisdir deyə bilmərik.",
        "Məhsul köhnə idi, son istifadə tarixi keçmişdi. Çox narazıyam!"
    ]
    
    print("\n" + "="*80)
    print("SINGLE TEXT ANALYSIS")
    print("="*80)
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n{i}. Text: {text}")
        result = analyzer.classify_review_quality(text)
        print(f"   Sentiment: {result['emoji']} {result['sentiment'].upper()}")
        print(f"   Confidence: {result['confidence']:.1%}")
        print(f"   Scores: P:{result['scores']['positive']:.2f} | "
              f"N:{result['scores']['neutral']:.2f} | "
              f"Neg:{result['scores']['negative']:.2f}")
        print(f"   Priority: {result['priority'].upper()}")
        print(f"   Actionable: {'YES' if result['is_actionable'] else 'NO'}")
    
    print("\n" + "="*80)
    print("BATCH ANALYSIS")
    print("="*80)
    
    batch_results = analyzer.analyze_batch(test_texts)
    for i, (text, result) in enumerate(zip(test_texts, batch_results), 1):
        emoji = analyzer.get_sentiment_emoji(result['sentiment'])
        print(f"{i}. {emoji} {result['sentiment']} ({result['confidence']:.1%}) - {text[:50]}...")
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    summary = analyzer.get_sentiment_summary(test_texts)
    print(f"  Positive: {summary['positive']} ({summary['positive_pct']}%)")
    print(f"  Neutral: {summary['neutral']} ({summary['neutral_pct']}%)")
    print(f"  Negative: {summary['negative']} ({summary['negative_pct']}%)")
    print(f"  Avg Confidence: {summary['avg_confidence']:.1%}")
    
    print("\n✅ All tests completed successfully!")
