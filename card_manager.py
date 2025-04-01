import json
import os
from typing import Dict, List, Optional
from datetime import datetime

class CardManager:
    def __init__(self, file_path: str = "flashcard_sets.json"):
        """
        Initialize the CardManager with a JSON file path.
        
        Args:
            file_path (str): Path to the JSON file storing flashcard sets
        """
        self.file_path = file_path
        self.card_sets = self._load_card_sets()
    
    def _load_card_sets(self) -> Dict:
        """Load card sets from JSON file or create new if doesn't exist."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        return {}
    
    def _save_card_sets(self):
        """Save card sets to JSON file."""
        with open(self.file_path, 'w', encoding='utf-8') as file:
            json.dump(self.card_sets, file, ensure_ascii=False, indent=4)
    
    def create_set(self, set_name: str, description: str = "") -> bool:
        """
        Create a new flashcard set.
        
        Args:
            set_name (str): Name of the new set
            description (str): Optional description of the set
            
        Returns:
            bool: True if created successfully, False if set already exists
        """
        if set_name in self.card_sets:
            return False
        
        self.card_sets[set_name] = {
            "description": description,
            "cards": {},
            "card_levels": {},  # Store Leitner system levels
            "next_reviews": {}  # Store next review times
        }
        self._save_card_sets()
        return True
    
    def delete_set(self, set_name: str) -> bool:
        """
        Delete a flashcard set.
        
        Args:
            set_name (str): Name of the set to delete
            
        Returns:
            bool: True if deleted successfully, False if set doesn't exist
        """
        if set_name not in self.card_sets:
            return False
        
        del self.card_sets[set_name]
        self._save_card_sets()
        return True
    
    def add_card(self, set_name: str, word: str, answer: str) -> bool:
        """
        Add a card to a set.
        
        Args:
            set_name (str): Name of the set to add to
            word (str): Word or question
            answer (str): Answer or translation
            
        Returns:
            bool: True if added successfully, False if set doesn't exist
        """
        if set_name not in self.card_sets:
            return False
        
        self.card_sets[set_name]["cards"][word] = answer
        self.card_sets[set_name]["card_levels"][word] = 0  # Initialize at level 0
        self.card_sets[set_name]["next_reviews"][word] = datetime.now().isoformat()
        self._save_card_sets()
        return True
    
    def remove_card(self, set_name: str, word: str) -> bool:
        """
        Remove a card from a set.
        
        Args:
            set_name (str): Name of the set
            word (str): Word to remove
            
        Returns:
            bool: True if removed successfully, False if set or word doesn't exist
        """
        if set_name not in self.card_sets or word not in self.card_sets[set_name]["cards"]:
            return False
        
        del self.card_sets[set_name]["cards"][word]
        del self.card_sets[set_name]["card_levels"][word]
        del self.card_sets[set_name]["next_reviews"][word]
        self._save_card_sets()
        return True
    
    def edit_card(self, set_name: str, word: str, new_word: str = None, new_answer: str = None) -> bool:
        """
        Edit a card in a set.
        
        Args:
            set_name (str): Name of the set
            word (str): Word to edit
            new_word (str, optional): New word if changing the word
            new_answer (str, optional): New answer if changing the answer
            
        Returns:
            bool: True if edited successfully, False if set or word doesn't exist
        """
        if set_name not in self.card_sets or word not in self.card_sets[set_name]["cards"]:
            return False
        
        if new_word and new_word != word:
            # Transfer card data to new word
            self.card_sets[set_name]["cards"][new_word] = (
                new_answer if new_answer else self.card_sets[set_name]["cards"][word]
            )
            self.card_sets[set_name]["card_levels"][new_word] = self.card_sets[set_name]["card_levels"][word]
            self.card_sets[set_name]["next_reviews"][new_word] = self.card_sets[set_name]["next_reviews"][word]
            
            # Remove old word data
            del self.card_sets[set_name]["cards"][word]
            del self.card_sets[set_name]["card_levels"][word]
            del self.card_sets[set_name]["next_reviews"][word]
        elif new_answer:
            self.card_sets[set_name]["cards"][word] = new_answer
            
        self._save_card_sets()
        return True
    
    def get_sets(self) -> List[str]:
        """Get list of all set names."""
        return list(self.card_sets.keys())
    
    def get_set_info(self, set_name: str) -> Optional[Dict]:
        """
        Get information about a specific set.
        
        Args:
            set_name (str): Name of the set
            
        Returns:
            Dict or None: Set information if exists, None otherwise
        """
        return self.card_sets.get(set_name)
    
    def get_cards(self, set_name: str) -> Optional[Dict]:
        """
        Get all cards in a set.
        
        Args:
            set_name (str): Name of the set
            
        Returns:
            Dict or None: Cards if set exists, None otherwise
        """
        set_info = self.card_sets.get(set_name)
        return set_info["cards"] if set_info else None
    
    def get_due_cards(self, set_name: str) -> List[str]:
        """
        Get list of cards due for review.
        
        Args:
            set_name (str): Name of the set
            
        Returns:
            List[str]: List of words due for review
        """
        if set_name not in self.card_sets:
            return []
            
        now = datetime.now()
        return [
            word for word, next_review in self.card_sets[set_name]["next_reviews"].items()
            if datetime.fromisoformat(next_review) <= now
        ]
    
    def update_card_schedule(self, set_name: str, word: str, next_review: datetime, new_level: int):
        """
        Update a card's schedule and level.
        
        Args:
            set_name (str): Name of the set
            word (str): The word to update
            next_review (datetime): Next review time
            new_level (int): New Leitner system level
        """
        if set_name in self.card_sets and word in self.card_sets[set_name]["cards"]:
            self.card_sets[set_name]["next_reviews"][word] = next_review.isoformat()
            self.card_sets[set_name]["card_levels"][word] = new_level
            self._save_card_sets()
    
    def get_card_level(self, set_name: str, word: str) -> int:
        """
        Get a card's current level.
        
        Args:
            set_name (str): Name of the set
            word (str): The word to check
            
        Returns:
            int: Current level of the card
        """
        if set_name in self.card_sets and word in self.card_sets[set_name]["card_levels"]:
            return self.card_sets[set_name]["card_levels"][word]
        return 0 