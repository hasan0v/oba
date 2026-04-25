"""
Train all ML models for OBA Smart Assistant
"""
import os
import sys
import pandas as pd

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ml.recommendation_engine import RecommendationEngine
from ml.complaint_classifier import ComplaintClassifier
from ml.demand_forecaster import DemandForecaster
from ml.sentiment_analyzer import SentimentAnalyzer

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'ml', 'models')

os.makedirs(MODELS_DIR, exist_ok=True)


def train_recommendation_model():
    """Train collaborative filtering recommendation model."""
    print("\n" + "="*60)
    print("Training Recommendation Engine")
    print("="*60)
    
    interactions_path = os.path.join(DATA_DIR, 'interactions.csv')
    
    if not os.path.exists(interactions_path):
        print(f"❌ Interactions data not found: {interactions_path}")
        print("   Run generate_data.py first!")
        return
    
    interactions_df = pd.read_csv(interactions_path)
    print(f"Loaded {len(interactions_df)} interactions")
    
    engine = RecommendationEngine()
    result = engine.train(interactions_df)
    
    model_path = os.path.join(MODELS_DIR, 'recommendation_model.pkl')
    engine.save_model(model_path)
    
    # Test recommendation only if model was trained
    if result is not None:
        sample_user = interactions_df['user_id'].iloc[0]
        recs = engine.get_recommendations(sample_user, n=5)
        print(f"\nSample recommendations for user {sample_user[:8]}...:")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. Product: {rec['product_id'][:8]}... (score: {rec['predicted_rating']:.2f})")
    else:
        print("\n⚠️  Skipping recommendation test (scikit-surprise not available)")
        print("   Install with: pip install scikit-surprise")
    
    print(f"\n✅ Recommendation model saved to {model_path}")


def train_complaint_classifier():
    """Train complaint classification model."""
    print("\n" + "="*60)
    print("Training Complaint Classifier")
    print("="*60)
    
    complaints_path = os.path.join(DATA_DIR, 'complaints.csv')
    
    if not os.path.exists(complaints_path):
        print(f"❌ Complaints data not found: {complaints_path}")
        print("   Run generate_data.py first!")
        return
    
    complaints_df = pd.read_csv(complaints_path)
    print(f"Loaded {len(complaints_df)} complaints")
    
    # Map category names to indices
    category_map = {
        'product': 0, 'service': 1, 'delivery': 2, 'pricing': 3, 'other': 4
    }
    
    texts = complaints_df['description'].tolist()
    labels = [category_map.get(cat, 4) for cat in complaints_df['category']]
    
    classifier = ComplaintClassifier()
    classifier.train(texts, labels)
    
    model_path = os.path.join(MODELS_DIR, 'complaint_classifier.pkl')
    classifier.save_model(model_path)
    
    # Test classification
    test_texts = [
        "Süd xarab idi, qoxusu var idi",
        "Kassir çox kobud danışdı",
        "Sifariş 3 saat gecikdi"
    ]
    
    print("\nSample classifications:")
    for text in test_texts:
        result = classifier.classify(text)
        print(f"  '{text[:40]}...'")
        print(f"    -> {result['category']} (priority: {result['priority']}, confidence: {result['confidence']:.2f})")
    
    print(f"\n✅ Complaint classifier saved to {model_path}")


def train_demand_forecaster():
    """Train demand forecasting models."""
    print("\n" + "="*60)
    print("Training Demand Forecaster")
    print("="*60)
    
    sales_path = os.path.join(DATA_DIR, 'sales_history.csv')
    
    if not os.path.exists(sales_path):
        print(f"❌ Sales history not found: {sales_path}")
        print("   Run generate_data.py first!")
        return
    
    sales_df = pd.read_csv(sales_path)
    print(f"Loaded {len(sales_df)} sales records")
    
    # Get unique products
    product_ids = sales_df['product_id'].unique()[:10]  # Train for first 10 products
    
    forecaster = DemandForecaster()
    
    for product_id in product_ids:
        product_sales = sales_df[sales_df['product_id'] == product_id].copy()
        if len(product_sales) >= 14:
            print(f"\nTraining model for product {product_id[:8]}...")
            forecaster.train(product_id, product_sales)
    
    # Save models
    model_prefix = os.path.join(MODELS_DIR, 'forecast_model')
    forecaster.save_models(model_prefix)
    
    # Test forecast
    if product_ids.size > 0:
        test_product = product_ids[0]
        print(f"\nSample 7-day forecast for product {test_product[:8]}...:")
        forecast = forecaster.forecast(test_product, periods=7)
        print(forecast[['date', 'predicted_quantity']].to_string(index=False))
        
        # Stockout risk
        risk = forecaster.detect_stockout_risk(test_product, current_stock=100)
        print(f"\nStockout risk: {risk['stockout_risk']}")
        print(f"Recommendation: {risk['recommendation']}")
    
    print(f"\n✅ Forecast models saved to {model_prefix}_*.pkl")


def test_sentiment_analyzer():
    """Test sentiment analyzer (no training needed for rule-based)."""
    print("\n" + "="*60)
    print("Testing Sentiment Analyzer")
    print("="*60)
    
    analyzer = SentimentAnalyzer()
    
    test_texts = [
        "Çox yaxşı məhsuldur, tövsiyə edirəm!",
        "Normal keyfiyyətdir, pis deyil",
        "Məhsul köhnə idi, bəyənmədim",
        "Əla xidmət, çox məmnunam",
        "Qiymət çox bahadır"
    ]
    
    print("\nSentiment analysis results:")
    for text in test_texts:
        result = analyzer.analyze(text)
        emoji = "😊" if result['sentiment'] == 'positive' else "😐" if result['sentiment'] == 'neutral' else "😞"
        print(f"  {emoji} '{text}'")
        print(f"     -> {result['sentiment']} (confidence: {result['confidence']:.2f})")
    
    print("\n✅ Sentiment analyzer ready (rule-based, no model file needed)")


def main():
    """Train all models."""
    print("\n" + "="*60)
    print("OBA Smart Assistant - Model Training")
    print("="*60)
    
    # Check if data exists
    if not os.path.exists(DATA_DIR):
        print(f"\n❌ Data directory not found: {DATA_DIR}")
        print("   Run generate_data.py first to create synthetic data!")
        return
    
    # Train models
    train_recommendation_model()
    train_complaint_classifier()
    train_demand_forecaster()
    test_sentiment_analyzer()
    
    print("\n" + "="*60)
    print("✅ All models trained successfully!")
    print(f"📁 Models saved to: {os.path.abspath(MODELS_DIR)}")
    print("="*60)


if __name__ == "__main__":
    main()
