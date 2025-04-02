import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os
import json

class SmartReview:
    def __init__(self, history_file="flashcard_history.csv", model_dir="models"):
        """
        Initialize the Smart Review system.
        
        Args:
            history_file (str): Path to the CSV file containing review history
            model_dir (str): Directory to save model files
        """
        self.history_file = history_file
        self.model_dir = model_dir
        self.model = None
        self.scaler = StandardScaler()
        self.min_data_points = 10
        self.last_training_size = 0
        self.model_version = 1
        self.model_metadata = {}
        
        # Create models directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        # Initial intervals for the Leitner system (in hours)
        self.base_intervals = [0, 24, 72, 168, 336, 672, 1344]  # 0h, 1d, 3d, 1w, 2w, 4w, 8w
        
        # Try to load existing model
        self.load_model()
        
    def _get_model_path(self, version=None):
        """Get the path for model files based on version."""
        if version is None:
            version = self.model_version
        return os.path.join(self.model_dir, f"model_v{version}")

    def _save_model_metadata(self):
        """Save model metadata to JSON file."""
        metadata = {
            'version': self.model_version,
            'last_training_size': self.last_training_size,
            'training_date': datetime.now().isoformat(),
            'feature_names': list(self._extract_features_template().keys()),
            'min_data_points': self.min_data_points,
            'performance': self.model_metadata.get('performance', {})
        }
        
        metadata_path = os.path.join(self.model_dir, 'model_metadata.json')
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=4)

    def _extract_features_template(self):
        """Return template of features for documentation."""
        return {
            'avg_success_rate': 0.0,
            'recent_success_rate': 0.0,
            'total_reviews': 0,
            'hour_of_day': 0,
            'day_of_week': 0,
            'last_interval': 0.0,
            'avg_interval': 0.0,
            'set_avg_success': 0.0
        }

    def _should_train_model(self, history_df):
        """
        Check if the model should be trained based on new data.
        
        Returns:
            bool: True if model should be trained, False otherwise
        """
        if history_df.empty:
            return False
            
        # Get current number of review entries
        current_size = len(history_df)
        
        # If we have no model or enough new data points, train the model
        should_train = (
            self.model is None or
            (current_size >= self.min_data_points and
             current_size > self.last_training_size * 1.2)  # 20% more data than last training
        )
        
        return should_train
        
    def _load_history(self):
        """Load and preprocess review history. Automatically trains model if needed."""
        if not os.path.exists(self.history_file):
            return pd.DataFrame()
        
        df = pd.read_csv(self.history_file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Check if we should train the model
        if self._should_train_model(df):
            print("Training model with updated data...")
            self.train_model()
            
        return df
    
    def _extract_features(self, history_df, card_word, set_name):
        """
        Extract features for ML model from review history.
        
        Args:
            history_df (DataFrame): Review history
            card_word (str): The word/question
            set_name (str): Name of the flashcard set
            
        Returns:
            dict: Features for prediction
        """
        if history_df.empty:
            return None
            
        # Filter history for this card
        card_history = history_df[history_df[card_word].notna()]
        
        if len(card_history) < 2:
            return None
            
        features = {
            # Performance metrics
            'avg_success_rate': card_history[card_word].mean(),
            'recent_success_rate': card_history[card_word].tail(3).mean(),
            'total_reviews': len(card_history),
            
            # Time patterns
            'hour_of_day': datetime.now().hour,
            'day_of_week': datetime.now().weekday(),
            
            # Intervals
            'last_interval': (datetime.now() - card_history['Timestamp'].iloc[-1]).total_seconds() / 3600,
            'avg_interval': np.mean([
                (t2 - t1).total_seconds() / 3600
                for t1, t2 in zip(card_history['Timestamp'], card_history['Timestamp'].iloc[1:])
            ]),
            
            # Set performance
            'set_avg_success': history_df[history_df['Set'] == set_name]['Score'].mean() / \
                             history_df[history_df['Set'] == set_name]['Total'].mean(),
        }
        
        return features
    
    def _prepare_training_data(self, history_df):
        """Prepare training data for the ML model."""
        X = []  # Features
        y = []  # Target (successful interval lengths)
        
        for set_name in history_df['Set'].unique():
            set_cards = [col for col in history_df.columns if col not in 
                        ['Timestamp', 'Set', 'Score', 'Total', 'Accuracy']]
            
            for card in set_cards:
                features = self._extract_features(history_df, card, set_name)
                if features is None:
                    continue
                
                # Get successful intervals (where the card was answered correctly)
                card_history = history_df[history_df[card].notna()]
                successful_intervals = []
                
                for i in range(len(card_history) - 1):
                    if card_history.iloc[i][card] == 1:  # If answered correctly
                        interval = (card_history['Timestamp'].iloc[i + 1] - 
                                  card_history['Timestamp'].iloc[i]).total_seconds() / 3600
                        if interval > 0:  # Ignore same-session reviews
                            successful_intervals.append(interval)
                
                if successful_intervals:
                    X.append(list(features.values()))
                    y.append(np.mean(successful_intervals))  # Use mean successful interval as target
        
        return np.array(X), np.array(y)
    
    def train_model(self):
        """Train the ML model on review history."""
        history_df = self._load_history()
        
        if history_df.empty:
            return False
            
        X, y = self._prepare_training_data(history_df)
        
        if len(X) < self.min_data_points:
            return False
            
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Update metadata
        self.last_training_size = len(history_df)
        self.model_version += 1
        self.model_metadata['performance'] = {
            'num_samples': len(X),
            'feature_importance': dict(zip(
                self._extract_features_template().keys(),
                self.model.feature_importances_.tolist()
            ))
        }
        
        # Save model files
        model_path = self._get_model_path()
        joblib.dump(self.model, f"{model_path}.joblib")
        joblib.dump(self.scaler, f"{model_path}_scaler.joblib")
        self._save_model_metadata()
        
        print(f"Model v{self.model_version} trained successfully with {len(X)} data points")
        return True
    
    def load_model(self):
        """Load the trained model if it exists."""
        # Load metadata first
        metadata_path = os.path.join(self.model_dir, 'model_metadata.json')
        if os.path.exists(metadata_path):
            try:
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
                self.model_version = self.model_metadata['version']
                self.last_training_size = self.model_metadata['last_training_size']
            except:
                print("Error loading model metadata, starting fresh")
                return False
        
        # Load model and scaler
        model_path = self._get_model_path()
        if os.path.exists(f"{model_path}.joblib"):
            try:
                self.model = joblib.load(f"{model_path}.joblib")
                self.scaler = joblib.load(f"{model_path}_scaler.joblib")
                print(f"Loaded model v{self.model_version} trained on {self.last_training_size} data points")
                return True
            except:
                print("Error loading model files, starting fresh")
                self.model = None
                self.model_version = 0
                self.last_training_size = 0
                return False
        return False
    
    def get_next_review_time(self, card_word, set_name, current_level=0):
        """
        Get the recommended next review time for a card.
        
        Args:
            card_word (str): The word/question
            set_name (str): Name of the flashcard set
            current_level (int): Current Leitner level of the card
            
        Returns:
            datetime: Recommended next review time
        """
        history_df = self._load_history()
        features = self._extract_features(history_df, card_word, set_name)
        
        if features is None or self.model is None:
            # Fall back to Leitner system if not enough data or no model
            hours = self.base_intervals[min(current_level, len(self.base_intervals) - 1)]
            return datetime.now() + timedelta(hours=hours)
        
        # Predict optimal interval using ML model
        X = np.array(list(features.values())).reshape(1, -1)
        X_scaled = self.scaler.transform(X)
        predicted_hours = max(1, self.model.predict(X_scaled)[0])  # Minimum 1 hour
        
        return datetime.now() + timedelta(hours=predicted_hours)
    
    def update_card_level(self, card_word, set_name, correct):
        """
        Update a card's level based on answer correctness.
        
        Args:
            card_word (str): The word/question
            set_name (str): Name of the flashcard set
            correct (bool): Whether the answer was correct
            
        Returns:
            int: New level
        """
        history_df = self._load_history()
        
        if history_df.empty:
            return 1 if correct else 0
            
        # Filter history for this card and set
        card_history = history_df[
            (history_df['Set'] == set_name) & 
            (history_df.apply(lambda row: card_word in row.index and pd.notna(row[card_word]), axis=1))
        ]
        
        current_level = len(card_history)
        
        if correct:
            return min(current_level + 1, len(self.base_intervals) - 1)
        else:
            return max(0, current_level - 1) 