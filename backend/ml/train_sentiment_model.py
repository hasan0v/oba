"""
Fine-tune allmalab/bert-small-aze on OBA reviews dataset
for better Azerbaijani sentiment analysis
"""
import os
import sys
import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from transformers import (
        AutoTokenizer, 
        AutoModelForSequenceClassification,
        TrainingArguments,
        Trainer
    )
    import torch
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
    from datasets import Dataset
    DEPS_AVAILABLE = True
except ImportError as e:
    logger.error(f"Missing dependency: {e}")
    logger.error("Please install: pip install transformers torch datasets scikit-learn")
    DEPS_AVAILABLE = False


class SentimentModelTrainer:
    """
    Fine-tune allmalab/bert-small-aze on OBA reviews dataset
    """
    
    def __init__(self, model_name: str = "allmalab/bert-small-aze"):
        """
        Initialize trainer with base model
        
        Args:
            model_name: HuggingFace model to fine-tune
        """
        if not DEPS_AVAILABLE:
            raise RuntimeError("Required dependencies not available")
        
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = None
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        logger.info(f"Using device: {self.device}")
        
    def prepare_dataset(self, csv_path: str):
        """
        Load and prepare dataset from CSV
        
        CSV should have columns: 'comment', 'sentiment'
        sentiment values: 'positive', 'neutral', 'negative'
        
        Args:
            csv_path: Path to CSV file with reviews
            
        Returns:
            train_dataset, val_dataset, test_dataset
        """
        logger.info(f"Loading data from {csv_path}")
        
        # Load data
        df = pd.read_csv(csv_path)
        
        # Handle different column names
        comment_col = None
        for col in ['comment', 'review', 'text', 'content']:
            if col in df.columns:
                comment_col = col
                break
        
        if comment_col is None:
            raise ValueError("No comment column found. Expected: comment, review, text, or content")
        
        # Check for sentiment column or infer from rating
        if 'sentiment' in df.columns:
            pass  # Use existing sentiment
        elif 'rating' in df.columns:
            # Infer sentiment from rating
            df['sentiment'] = df['rating'].apply(lambda x: 
                'positive' if x >= 4 else ('negative' if x <= 2 else 'neutral')
            )
        else:
            raise ValueError("No sentiment or rating column found")
        
        # Rename comment column
        df = df.rename(columns={comment_col: 'comment'})
        
        # Map sentiment to labels
        label_map = {'negative': 0, 'neutral': 1, 'positive': 2}
        df['label'] = df['sentiment'].map(label_map)
        
        # Remove invalid rows
        df = df.dropna(subset=['comment', 'label'])
        df = df[df['comment'].str.len() > 0]
        
        logger.info(f"Total valid samples: {len(df)}")
        logger.info(f"Label distribution:\n{df['sentiment'].value_counts()}")
        
        # Split train/val/test (70/15/15)
        train_df, temp_df = train_test_split(
            df, test_size=0.3, random_state=42, 
            stratify=df['label'] if len(df) > 10 else None
        )
        val_df, test_df = train_test_split(
            temp_df, test_size=0.5, random_state=42,
            stratify=temp_df['label'] if len(temp_df) > 10 else None
        )
        
        logger.info(f"Dataset split:")
        logger.info(f"  Train: {len(train_df)} samples")
        logger.info(f"  Val: {len(val_df)} samples")
        logger.info(f"  Test: {len(test_df)} samples")
        
        # Convert to HuggingFace Dataset
        train_dataset = Dataset.from_pandas(train_df[['comment', 'label']].reset_index(drop=True))
        val_dataset = Dataset.from_pandas(val_df[['comment', 'label']].reset_index(drop=True))
        test_dataset = Dataset.from_pandas(test_df[['comment', 'label']].reset_index(drop=True))
        
        # Tokenize
        def tokenize_function(examples):
            return self.tokenizer(
                examples['comment'],
                padding='max_length',
                truncation=True,
                max_length=128  # Shorter for faster training
            )
        
        logger.info("Tokenizing datasets...")
        train_dataset = train_dataset.map(tokenize_function, batched=True)
        val_dataset = val_dataset.map(tokenize_function, batched=True)
        test_dataset = test_dataset.map(tokenize_function, batched=True)
        
        # Set format for PyTorch
        train_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        val_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        test_dataset.set_format('torch', columns=['input_ids', 'attention_mask', 'label'])
        
        return train_dataset, val_dataset, test_dataset
    
    def compute_metrics(self, eval_pred):
        """Compute evaluation metrics"""
        predictions, labels = eval_pred
        predictions = np.argmax(predictions, axis=1)
        
        return {
            'accuracy': accuracy_score(labels, predictions),
            'f1': f1_score(labels, predictions, average='weighted'),
            'precision': precision_score(labels, predictions, average='weighted', zero_division=0),
            'recall': recall_score(labels, predictions, average='weighted', zero_division=0)
        }
    
    def train(self, train_dataset, val_dataset, output_dir: str = "./models/sentiment_finetuned"):
        """
        Fine-tune model on OBA reviews
        
        Args:
            train_dataset: Training dataset
            val_dataset: Validation dataset
            output_dir: Directory to save model
            
        Returns:
            Trainer object
        """
        logger.info(f"Loading base model: {self.model_name}")
        
        # Load model with classification head
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=3,
            ignore_mismatched_sizes=True
        )
        self.model.to(self.device)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=3,
            per_device_train_batch_size=16,
            per_device_eval_batch_size=32,
            warmup_steps=100,
            weight_decay=0.01,
            logging_dir=f'{output_dir}/logs',
            logging_steps=50,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="f1",
            greater_is_better=True,
            save_total_limit=2,
            learning_rate=2e-5,
            fp16=torch.cuda.is_available(),  # Use FP16 if GPU available
            report_to="none",  # Disable wandb/tensorboard
        )
        
        # Create Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=val_dataset,
            compute_metrics=self.compute_metrics
        )
        
        # Train
        logger.info("\n🚀 Starting training...")
        trainer.train()
        
        # Save final model
        logger.info(f"\n💾 Saving model to {output_dir}")
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        return trainer
    
    def evaluate(self, trainer, test_dataset):
        """
        Evaluate on test set
        
        Args:
            trainer: Trained Trainer object
            test_dataset: Test dataset
            
        Returns:
            Evaluation results
        """
        logger.info("\n📊 Evaluating on test set...")
        results = trainer.evaluate(test_dataset)
        
        print("\n" + "="*50)
        print("TEST RESULTS")
        print("="*50)
        print(f"  Accuracy:  {results['eval_accuracy']:.4f}")
        print(f"  F1 Score:  {results['eval_f1']:.4f}")
        print(f"  Precision: {results['eval_precision']:.4f}")
        print(f"  Recall:    {results['eval_recall']:.4f}")
        print("="*50)
        
        return results
    
    def predict(self, texts: list):
        """
        Make predictions on new texts
        
        Args:
            texts: List of texts to classify
            
        Returns:
            List of predictions
        """
        if self.model is None:
            raise RuntimeError("Model not trained. Call train() first.")
        
        self.model.eval()
        predictions = []
        
        for text in texts:
            inputs = self.tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            ).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=1)[0]
                pred_class = torch.argmax(probs).item()
            
            sentiment_map = {0: 'negative', 1: 'neutral', 2: 'positive'}
            predictions.append({
                'text': text[:50] + '...' if len(text) > 50 else text,
                'sentiment': sentiment_map[pred_class],
                'confidence': float(probs[pred_class])
            })
        
        return predictions


def main():
    """Main training pipeline"""
    print("\n" + "="*60)
    print("🎓 OBA Sentiment Model Fine-tuning")
    print("="*60)
    
    if not DEPS_AVAILABLE:
        print("❌ Required dependencies not installed!")
        print("Run: pip install transformers torch datasets scikit-learn")
        return
    
    # Initialize trainer
    trainer = SentimentModelTrainer()
    
    # Path to reviews data
    data_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'reviews.csv')
    
    if not os.path.exists(data_path):
        print(f"❌ Data file not found: {data_path}")
        print("Please generate data first using generate_data.py")
        return
    
    # Prepare dataset
    print("\n📚 Preparing dataset...")
    train_ds, val_ds, test_ds = trainer.prepare_dataset(data_path)
    
    # Train
    output_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'models', 'sentiment_finetuned')
    trained = trainer.train(train_ds, val_ds, output_dir)
    
    # Evaluate
    trainer.evaluate(trained, test_ds)
    
    # Test predictions
    print("\n🧪 Testing predictions...")
    test_texts = [
        "Bu məhsul çox yaxşıdır!",
        "Keyfiyyət pisdir, bəyənmədim",
        "Normal məhsuldur"
    ]
    
    predictions = trainer.predict(test_texts)
    for pred in predictions:
        emoji = {'positive': '😊', 'neutral': '😐', 'negative': '😞'}[pred['sentiment']]
        print(f"  {emoji} {pred['sentiment']} ({pred['confidence']:.1%}): {pred['text']}")
    
    print(f"\n✅ Training completed! Model saved to {output_dir}")
    print("To use the fine-tuned model, update sentiment_analyzer.py:")
    print(f'  SentimentAnalyzer(model_name="{output_dir}")')


if __name__ == "__main__":
    main()
