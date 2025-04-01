class Flashcards:
    def __init__(self, cards):
        """
        Initialize the Flashcards class with a dictionary of cards.
        
        Args:
            cards (dict): A dictionary where keys are words and values are answers
        """
        self.cards = cards
        
    # Add a method to store game history
    def save_game_history(self, score, total, results=None):
        """
        Save the game results to a CSV history file.
        
        Args:
            score (int): The number of correct answers
            total (int): The total number of questions
            results (dict, optional): Dictionary with words as keys and 0/1 as values
                                     (0 for incorrect, 1 for correct)
        """
        import datetime
        import csv
        import os
        
        # Create a timestamp for the game
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accuracy = (score/total)*100 if total > 0 else 0
        
        # Define the history file path
        history_file = "flashcard_history.csv"
        
        # Check if file exists to determine if we need to write headers
        file_exists = os.path.isfile(history_file)
        
        with open(history_file, "a", newline='') as file:
            writer = csv.writer(file)
            
            # Write headers if file is new
            if not file_exists:
                headers = ["Timestamp", "Score", "Total", "Accuracy"]
                if results:
                    # Add all flashcard words as column headers
                    headers.extend(list(results.keys()))
                writer.writerow(headers)
            
            # Prepare the row data
            row_data = [timestamp, score, total, f"{accuracy:.2f}%"]
            if results:
                # Add 0 for incorrect answers and 1 for correct answers for each word
                row_data.extend([results.get(word, 0) for word in results.keys()])
            
            # Write the data row
            writer.writerow(row_data)
        
        print(f"Game history saved to {history_file}")
    # Update the game method to save history
    def game(self):
        """
        Start a flashcard game in the terminal.
        Users are prompted with words and need to provide answers.
        Game history is saved at the end.
        """
        import random
        
        print("Welcome to Flashcards Game!")
        print("Type 'exit' to quit the game at any time.")
        print("-" * 40)
        
        score = 0
        total = len(self.cards)
        
        # Convert dictionary items to a list and shuffle them
        flashcard_items = list(self.cards.items())
        random.shuffle(flashcard_items)
        
        for word, answer in flashcard_items:
            print(f"\nWord: {word}")
            user_answer = input("Your answer: ")
            
            if user_answer.lower() == 'exit':
                print("\nGame ended by user.")
                break
            
            if user_answer.lower() == answer.lower():
                print("Correct!")
                score += 1
            else:
                print(f"Incorrect. The correct answer is: {answer}")
        
        print("\n" + "-" * 40)
        print(f"Game over! Your score: {score}/{total}")
        print(f"Accuracy: {(score/total)*100:.2f}%")
        
        # Save the game history
        self.save_game_history(score, total)
        
        
# Example usage:
if __name__ == "__main__":
    cards = {
        "apple": "manzana",
        "hello": "hola",
        "goodbye": "adiós",
        "cat": "gato",
        "dog": "perro"
    }
    
    flashcard_game = Flashcards(cards)
    flashcard_game.game() 