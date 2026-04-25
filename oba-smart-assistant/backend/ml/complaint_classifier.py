"""
Complaint Classification using NLP
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional
import joblib
import os
import re

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.linear_model import LogisticRegression
    from sklearn.pipeline import Pipeline
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Using rule-based classification.")


class ComplaintClassifier:
    """
    AI-powered complaint classification system.
    
    Automatically categorizes customer complaints into predefined categories
    and assigns priority levels based on content analysis.
    """
    
    # Category definitions
    CATEGORIES = ['product', 'service', 'delivery', 'pricing', 'other']
    
    # Priority keywords for rule-based priority assignment
    HIGH_PRIORITY_KEYWORDS = [
        'zəhərləndim', 'xəstələndim', 'qurd', 'çürük', 'təhlükəli',
        'allergiya', 'xəsarət', 'yanıq', 'infeksiya', 'poison',
        'sick', 'hospital', 'emergency', 'danger', 'harmful'
    ]
    
    MEDIUM_PRIORITY_KEYWORDS = [
        'gecikdi', 'kobud', 'çirkli', 'səhv', 'xarab', 'köhnə',
        'qırıq', 'sınıq', 'zədə', 'açılmış', 'sızıntı',
        'delayed', 'rude', 'dirty', 'wrong', 'broken', 'damaged'
    ]
    
    # Category-specific keywords for rule-based classification
    CATEGORY_KEYWORDS = {
        'product': [
            'məhsul', 'süd', 'çörək', 'meyvə', 'tərəvəz', 'ət', 'balıq',
            'xarab', 'köhnə', 'tarix', 'keyfiyyət', 'dad', 'iy', 'qoxu',
            'çürük', 'bayat', 'qurd', 'küf', 'product', 'quality', 'expired'
        ],
        'service': [
            'xidmət', 'işçi', 'kassir', 'satıcı', 'növbə', 'gözləmə',
            'kobud', 'hörmət', 'davranış', 'kömək', 'cavab', 'münasibət',
            'service', 'staff', 'cashier', 'rude', 'wait', 'queue'
        ],
        'delivery': [
            'çatdırılma', 'kuryer', 'gecikdi', 'ünvan', 'sifariş',
            'gəlmədi', 'itdi', 'zədələndi', 'səhv', 'vaxt',
            'delivery', 'courier', 'late', 'address', 'order', 'missing'
        ],
        'pricing': [
            'qiymət', 'endirim', 'baha', 'hesab', 'çek', 'ödəniş',
            'kampaniya', 'artıq', 'düzgün deyil', 'fərq', 'qaytarma',
            'price', 'discount', 'expensive', 'overcharge', 'payment'
        ]
    }
    
    def __init__(self):
        self.pipeline = None
        self.is_trained = False
        
    def train(self, texts: List[str], labels: List[int], test_size: float = 0.2) -> Optional[Pipeline]:
        """
        Train the complaint classifier.
        
        Args:
            texts: List of complaint texts
            labels: List of category indices (0-4)
            test_size: Proportion of data to use for testing
            
        Returns:
            Trained pipeline or None if training fails
        """
        if not SKLEARN_AVAILABLE:
            print("Cannot train: scikit-learn not installed")
            return None
        
        if len(texts) < 10:
            print("Cannot train: Need at least 10 samples")
            return None
        
        # Create pipeline with TF-IDF and Logistic Regression
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=2000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,
                class_weight='balanced',
                random_state=42
            ))
        ])
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels, test_size=test_size, random_state=42, stratify=labels
        )
        
        # Train
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        
        print("Complaint Classifier Training Results:")
        print("-" * 50)
        print(f"Training samples: {len(X_train)}")
        print(f"Test samples: {len(X_test)}")
        print(f"\nClassification Report:")
        print(classification_report(
            y_test, y_pred, 
            target_names=self.CATEGORIES,
            zero_division=0
        ))
        
        return self.pipeline
    
    def classify(self, text: str) -> Dict:
        """
        Classify a complaint.
        
        Args:
            text: Complaint text
            
        Returns:
            Dictionary with category, priority, and confidence
        """
        if not text or not text.strip():
            return {
                'category': 'other',
                'priority': 'low',
                'confidence': 0.0
            }
        
        # Get category
        if self.is_trained and self.pipeline:
            category_result = self._classify_with_model(text)
        else:
            category_result = self._classify_rule_based(text)
        
        # Get priority
        priority = self._assign_priority(text, category_result['confidence'])
        
        return {
            'category': category_result['category'],
            'priority': priority,
            'confidence': category_result['confidence'],
            'category_scores': category_result.get('scores', {})
        }
    
    def _classify_with_model(self, text: str) -> Dict:
        """Classify using trained model."""
        try:
            # Get prediction
            prediction = self.pipeline.predict([text])[0]
            
            # Get probabilities
            probabilities = self.pipeline.predict_proba([text])[0]
            confidence = float(max(probabilities))
            
            # Get all category scores
            scores = {
                self.CATEGORIES[i]: round(float(p), 3)
                for i, p in enumerate(probabilities)
            }
            
            return {
                'category': self.CATEGORIES[prediction],
                'confidence': round(confidence, 3),
                'scores': scores
            }
            
        except Exception as e:
            print(f"Model classification failed: {e}")
            return self._classify_rule_based(text)
    
    def _classify_rule_based(self, text: str) -> Dict:
        """Classify using keyword-based rules."""
        text_lower = text.lower()
        
        # Count keyword matches for each category
        category_scores = {}
        
        for category, keywords in self.CATEGORY_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            category_scores[category] = score
        
        # Find best matching category
        if max(category_scores.values()) == 0:
            return {
                'category': 'other',
                'confidence': 0.5,
                'scores': {cat: 0.2 for cat in self.CATEGORIES}
            }
        
        best_category = max(category_scores, key=category_scores.get)
        total_score = sum(category_scores.values())
        
        # Normalize scores
        normalized_scores = {
            cat: round(score / total_score, 3) if total_score > 0 else 0.2
            for cat, score in category_scores.items()
        }
        normalized_scores['other'] = 0.1
        
        return {
            'category': best_category,
            'confidence': normalized_scores[best_category],
            'scores': normalized_scores
        }
    
    def _assign_priority(self, text: str, confidence: float) -> str:
        """
        Assign priority based on text content and confidence.
        
        Args:
            text: Complaint text
            confidence: Classification confidence
            
        Returns:
            Priority level ('low', 'medium', 'high', 'critical')
        """
        text_lower = text.lower()
        
        # Check for high priority keywords (health/safety issues)
        if any(kw in text_lower for kw in self.HIGH_PRIORITY_KEYWORDS):
            return 'critical'
        
        # Check for medium priority keywords
        if any(kw in text_lower for kw in self.MEDIUM_PRIORITY_KEYWORDS):
            return 'high'
        
        # Low confidence might indicate complex issue
        if confidence < 0.4:
            return 'medium'
        
        return 'low'
    
    def batch_classify(self, texts: List[str]) -> List[Dict]:
        """
        Classify multiple complaints.
        
        Args:
            texts: List of complaint texts
            
        Returns:
            List of classification results
        """
        return [self.classify(text) for text in texts]
    
    def get_category_summary(self, texts: List[str]) -> Dict:
        """
        Get summary of complaint categories.
        
        Args:
            texts: List of complaint texts
            
        Returns:
            Summary statistics
        """
        results = self.batch_classify(texts)
        
        categories = [r['category'] for r in results]
        priorities = [r['priority'] for r in results]
        
        total = len(results)
        
        return {
            'total': total,
            'by_category': {cat: categories.count(cat) for cat in self.CATEGORIES},
            'by_priority': {
                'critical': priorities.count('critical'),
                'high': priorities.count('high'),
                'medium': priorities.count('medium'),
                'low': priorities.count('low')
            },
            'avg_confidence': round(
                sum(r['confidence'] for r in results) / total if total > 0 else 0,
                3
            )
        }
    
    def save_model(self, filepath: str):
        """Save trained model to disk."""
        if not self.pipeline:
            raise ValueError("No model to save. Train the model first.")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(self.pipeline, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> Pipeline:
        """Load trained model from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        self.pipeline = joblib.load(filepath)
        self.is_trained = True
        print(f"Model loaded from {filepath}")
        return self.pipeline


# Example usage
if __name__ == "__main__":
    classifier = ComplaintClassifier()
    
    # Test texts
    test_complaints = [
        "Süd çox tez xarab oldu, 2 gün əvvəl aldım amma iyi var",
        "Kassir çox kobud danışdı, hörmət yoxdur",
        "Sifariş 2 saat gecikdi, məhsullar da soyuq idi",
        "Qiymət vitrinlə çekdə fərqlidir, düzəldin",
        "Mağazada parkinq yeri tapmaq çox çətindir"
    ]
    
    print("Complaint Classification Results:")
    print("=" * 60)
    
    for complaint in test_complaints:
        result = classifier.classify(complaint)
        print(f"\nComplaint: {complaint}")
        print(f"  Category: {result['category']}")
        print(f"  Priority: {result['priority']}")
        print(f"  Confidence: {result['confidence']}")
    
    # Summary
    summary = classifier.get_category_summary(test_complaints)
    print(f"\n{'='*60}")
    print("Summary:")
    print(f"  By Category: {summary['by_category']}")
    print(f"  By Priority: {summary['by_priority']}")
