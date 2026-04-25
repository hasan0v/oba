"""
Collaborative Filtering Recommendation Engine using SVD
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import joblib
import os

try:
    from surprise import SVD, Dataset, Reader
    from surprise.model_selection import train_test_split
    from surprise import accuracy
    SURPRISE_AVAILABLE = True
except ImportError:
    SURPRISE_AVAILABLE = False
    print("Warning: scikit-surprise not installed. Recommendation features will be limited.")


class RecommendationEngine:
    """
    Collaborative Filtering Recommendation Engine using SVD algorithm.
    
    This engine analyzes user-product interactions (ratings, purchases, views)
    to generate personalized product recommendations.
    """
    
    def __init__(self):
        self.model = None
        self.trainset = None
        self.user_mapping = {}
        self.product_mapping = {}
        self.reverse_product_mapping = {}
        
    def train(self, interactions_df: pd.DataFrame) -> Optional['SVD']:
        """
        Train collaborative filtering model.
        
        Args:
            interactions_df: DataFrame with columns: user_id, product_id, rating (1-5)
            
        Returns:
            Trained SVD model or None if training fails
        """
        if not SURPRISE_AVAILABLE:
            print("Cannot train: scikit-surprise not installed")
            return None
            
        if interactions_df.empty:
            print("Cannot train: Empty interactions dataframe")
            return None
        
        # Create mappings for user and product IDs
        unique_users = interactions_df['user_id'].unique()
        unique_products = interactions_df['product_id'].unique()
        
        self.user_mapping = {uid: idx for idx, uid in enumerate(unique_users)}
        self.product_mapping = {pid: idx for idx, pid in enumerate(unique_products)}
        self.reverse_product_mapping = {idx: pid for pid, idx in self.product_mapping.items()}
        
        # Prepare data for Surprise
        reader = Reader(rating_scale=(1, 5))
        data = Dataset.load_from_df(
            interactions_df[['user_id', 'product_id', 'rating']], 
            reader
        )
        
        # Train-test split
        trainset, testset = train_test_split(data, test_size=0.2, random_state=42)
        
        # Train SVD model
        self.model = SVD(
            n_factors=50,      # Number of latent factors
            n_epochs=20,       # Number of training iterations
            lr_all=0.005,      # Learning rate
            reg_all=0.02,      # Regularization term
            random_state=42
        )
        self.model.fit(trainset)
        self.trainset = trainset
        
        # Evaluate
        predictions = self.model.test(testset)
        rmse = accuracy.rmse(predictions, verbose=False)
        mae = accuracy.mae(predictions, verbose=False)
        
        print(f"Model trained successfully!")
        print(f"  - RMSE: {rmse:.4f}")
        print(f"  - MAE: {mae:.4f}")
        print(f"  - Users: {len(unique_users)}")
        print(f"  - Products: {len(unique_products)}")
        print(f"  - Interactions: {len(interactions_df)}")
        
        return self.model
    
    def get_recommendations(
        self, 
        user_id: str, 
        n: int = 10,
        exclude_purchased: bool = True
    ) -> List[Dict]:
        """
        Get top N product recommendations for a user.
        
        Args:
            user_id: User identifier
            n: Number of recommendations to return
            exclude_purchased: Whether to exclude already purchased products
            
        Returns:
            List of dictionaries with product_id and predicted_rating
        """
        if not self.model:
            raise ValueError("Model not trained yet. Call train() first.")
        
        if not SURPRISE_AVAILABLE:
            return []
        
        # Get all products
        all_products = list(self.product_mapping.keys())
        
        # Get products user has already interacted with (to optionally exclude)
        user_products = set()
        if exclude_purchased and self.trainset:
            try:
                user_inner_id = self.trainset.to_inner_uid(user_id)
                user_products = set(
                    self.trainset.to_raw_iid(item)
                    for item in self.trainset.ur[user_inner_id]
                )
            except ValueError:
                # User not in training set - new user
                pass
        
        # Predict ratings for all products
        predictions = []
        for product_id in all_products:
            if exclude_purchased and product_id in user_products:
                continue
                
            pred = self.model.predict(user_id, product_id)
            predictions.append({
                'product_id': product_id,
                'predicted_rating': round(pred.est, 3)
            })
        
        # Sort by predicted rating (descending)
        predictions.sort(key=lambda x: x['predicted_rating'], reverse=True)
        
        # Return top N
        return predictions[:n]
    
    def get_similar_products(self, product_id: str, n: int = 10) -> List[Dict]:
        """
        Get products similar to a given product based on latent factors.
        
        Args:
            product_id: Product identifier
            n: Number of similar products to return
            
        Returns:
            List of dictionaries with product_id and similarity score
        """
        if not self.model or not SURPRISE_AVAILABLE:
            return []
        
        try:
            # Get product's latent factors
            inner_id = self.trainset.to_inner_iid(product_id)
            product_factors = self.model.qi[inner_id]
            
            # Calculate cosine similarity with all other products
            similarities = []
            for other_id, idx in self.product_mapping.items():
                if other_id == product_id:
                    continue
                    
                try:
                    other_inner_id = self.trainset.to_inner_iid(other_id)
                    other_factors = self.model.qi[other_inner_id]
                    
                    # Cosine similarity
                    similarity = np.dot(product_factors, other_factors) / (
                        np.linalg.norm(product_factors) * np.linalg.norm(other_factors)
                    )
                    
                    similarities.append({
                        'product_id': other_id,
                        'similarity': round(float(similarity), 3)
                    })
                except ValueError:
                    continue
            
            # Sort by similarity (descending)
            similarities.sort(key=lambda x: x['similarity'], reverse=True)
            
            return similarities[:n]
            
        except ValueError:
            return []
    
    def save_model(self, filepath: str):
        """Save model and mappings to disk."""
        model_data = {
            'model': self.model,
            'trainset': self.trainset,
            'user_mapping': self.user_mapping,
            'product_mapping': self.product_mapping,
            'reverse_product_mapping': self.reverse_product_mapping
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump(model_data, filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath: str) -> 'SVD':
        """Load model and mappings from disk."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
            
        model_data = joblib.load(filepath)
        
        self.model = model_data['model']
        self.trainset = model_data.get('trainset')
        self.user_mapping = model_data.get('user_mapping', {})
        self.product_mapping = model_data.get('product_mapping', {})
        self.reverse_product_mapping = model_data.get('reverse_product_mapping', {})
        
        print(f"Model loaded from {filepath}")
        return self.model


# Example usage
if __name__ == "__main__":
    # Load interaction data
    data_path = '../data/interactions.csv'
    
    if os.path.exists(data_path):
        interactions = pd.read_csv(data_path)
        
        # Train model
        engine = RecommendationEngine()
        engine.train(interactions)
        
        # Save model
        engine.save_model('models/recommendation_model.pkl')
        
        # Get recommendations for a sample user
        sample_user = interactions['user_id'].iloc[0]
        recs = engine.get_recommendations(user_id=sample_user, n=10)
        print(f"\nTop 10 recommendations for user {sample_user}:")
        for i, rec in enumerate(recs, 1):
            print(f"  {i}. {rec['product_id']} (predicted rating: {rec['predicted_rating']})")
    else:
        print(f"Data file not found: {data_path}")
        print("Run generate_data.py first to create synthetic data.")
