import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
import joblib
import os

class SmartReview:
    def __init__(self, history_file="flashcard_history.csv", model_file="review_model.joblib"):
        """
        Initialize the Smart Review system.
        
        Args:
            history_file (str): Path to the CSV file containing review history
            model_file (str): Path to save/load the trained model
        """
        self.history_file = history_file
        self.model_file = model_file
        self.model = None
        self.scaler = StandardScaler()
        
        # Initial intervals for the Leitner system (in hours)
        self.base_intervals = [0, 24, 72, 168, 336, 672, 1344]  # 0h, 1d, 3d, 1w, 2w, 4w, 8w
        
    def _load_history(self):
        """Load and preprocess review history."""
        if not os.path.exists(self.history_file):
            return pd.DataFrame()
        
        df = pd.read_csv(self.history_file)
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
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
        
        if len(X) < 10:  # Need minimum amount of data
            return False
            
        # Scale features
        X_scaled = self.scaler.fit_transform(X)
        
        # Train model
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self.model.fit(X_scaled, y)
        
        # Save model and scaler
        joblib.dump((self.model, self.scaler), self.model_file)
        return True
    
    def load_model(self):
        """Load the trained model if it exists."""
        if os.path.exists(self.model_file):
            self.model, self.scaler = joblib.load(self.model_file)
            return True
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
        card_history = history_df[history_df[card_word].notna()]
        current_level = len(card_history) - 1
        
        if correct:
            return min(current_level + 1, len(self.base_intervals) - 1)
        else:
            return max(0, current_level - 1) 