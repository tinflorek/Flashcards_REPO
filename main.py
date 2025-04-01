from card_manager import CardManager
import random
import os

class Flashcards:
    def __init__(self, card_manager: CardManager, current_set: str = None):
        """
        Initialize the Flashcards class with a CardManager instance.
        
        Args:
            card_manager (CardManager): Instance of CardManager for handling card sets
            current_set (str, optional): Name of the current flashcard set
        """
        self.card_manager = card_manager
        self.current_set = current_set
        
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
        
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        accuracy = (score/total)*100 if total > 0 else 0
        
        history_file = "flashcard_history.csv"
        file_exists = os.path.isfile(history_file)
        
        with open(history_file, "a", newline='') as file:
            writer = csv.writer(file)
            
            if not file_exists:
                headers = ["Timestamp", "Set", "Score", "Total", "Accuracy"]
                if results:
                    headers.extend(list(results.keys()))
                writer.writerow(headers)
            
            row_data = [timestamp, self.current_set, score, total, f"{accuracy:.2f}%"]
            if results:
                row_data.extend([results.get(word, 0) for word in results.keys()])
            
            writer.writerow(row_data)
        
        print(f"\nGame history saved to {history_file}")

    def game(self):
        """Start a flashcard game with the current set."""
        if not self.current_set:
            print("\nNo flashcard set selected. Please select a set first.")
            return
            
        cards = self.card_manager.get_cards(self.current_set)
        if not cards:
            print(f"\nNo cards found in set '{self.current_set}'.")
            return
            
        print(f"\nStarting game with set: {self.current_set}")
        print("Type 'exit' to quit the game at any time.")
        print("-" * 40)
        
        score = 0
        total = len(cards)
        results = {}
        
        flashcard_items = list(cards.items())
        random.shuffle(flashcard_items)
        
        for word, answer in flashcard_items:
            print(f"\nWord: {word}")
            user_answer = input("Your answer: ")
            
            if user_answer.lower() == 'exit':
                print("\nGame ended by user.")
                break
            
            correct = user_answer.lower() == answer.lower()
            results[word] = 1 if correct else 0
            
            if correct:
                print("Correct!")
                score += 1
            else:
                print(f"Incorrect. The correct answer is: {answer}")
        
        print("\n" + "-" * 40)
        print(f"Game over! Your score: {score}/{total}")
        print(f"Accuracy: {(score/total)*100:.2f}%")
        
        self.save_game_history(score, total, results)

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu(title: str, options: list):
    """Print a menu with numbered options."""
    clear_screen()
    print(f"\n{title}")
    print("-" * 40)
    for i, option in enumerate(options, 1):
        print(f"{i}. {option}")
    print("-" * 40)

def manage_sets(card_manager: CardManager):
    """Menu for managing flashcard sets."""
    while True:
        options = [
            "Create new set",
            "Delete set",
            "View sets",
            "Back to main menu"
        ]
        print_menu("Manage Sets", options)
        
        choice = input("Enter your choice (1-4): ")
        
        if choice == "1":
            name = input("\nEnter set name: ")
            desc = input("Enter set description (optional): ")
            if card_manager.create_set(name, desc):
                print(f"\nSet '{name}' created successfully!")
            else:
                print(f"\nSet '{name}' already exists!")
                
        elif choice == "2":
            sets = card_manager.get_sets()
            if not sets:
                print("\nNo sets available to delete!")
                continue
                
            print("\nAvailable sets:")
            for i, set_name in enumerate(sets, 1):
                print(f"{i}. {set_name}")
            
            try:
                idx = int(input("\nEnter set number to delete: ")) - 1
                if 0 <= idx < len(sets):
                    if card_manager.delete_set(sets[idx]):
                        print(f"\nSet '{sets[idx]}' deleted successfully!")
                else:
                    print("\nInvalid set number!")
            except ValueError:
                print("\nPlease enter a valid number!")
                
        elif choice == "3":
            sets = card_manager.get_sets()
            if not sets:
                print("\nNo sets available!")
            else:
                print("\nAvailable sets:")
                for set_name in sets:
                    info = card_manager.get_set_info(set_name)
                    cards = len(info["cards"])
                    desc = info["description"] or "No description"
                    print(f"\n{set_name}:")
                    print(f"  Description: {desc}")
                    print(f"  Cards: {cards}")
            input("\nPress Enter to continue...")
            
        elif choice == "4":
            break

def manage_cards(card_manager: CardManager, set_name: str):
    """Menu for managing cards in a set."""
    while True:
        options = [
            "Add card",
            "Remove card",
            "Edit card",
            "View cards",
            "Back to main menu"
        ]
        print_menu(f"Manage Cards - {set_name}", options)
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            word = input("\nEnter word/question: ")
            answer = input("Enter answer/translation: ")
            if card_manager.add_card(set_name, word, answer):
                print(f"\nCard added successfully!")
            else:
                print(f"\nFailed to add card!")
                
        elif choice == "2":
            cards = card_manager.get_cards(set_name)
            if not cards:
                print("\nNo cards available to remove!")
                continue
                
            print("\nAvailable cards:")
            card_list = list(cards.keys())
            for i, word in enumerate(card_list, 1):
                print(f"{i}. {word}")
            
            try:
                idx = int(input("\nEnter card number to remove: ")) - 1
                if 0 <= idx < len(card_list):
                    if card_manager.remove_card(set_name, card_list[idx]):
                        print(f"\nCard '{card_list[idx]}' removed successfully!")
                else:
                    print("\nInvalid card number!")
            except ValueError:
                print("\nPlease enter a valid number!")
                
        elif choice == "3":
            cards = card_manager.get_cards(set_name)
            if not cards:
                print("\nNo cards available to edit!")
                continue
                
            print("\nAvailable cards:")
            card_list = list(cards.keys())
            for i, word in enumerate(card_list, 1):
                print(f"{i}. {word}")
            
            try:
                idx = int(input("\nEnter card number to edit: ")) - 1
                if 0 <= idx < len(card_list):
                    word = card_list[idx]
                    print(f"\nEditing card: {word} -> {cards[word]}")
                    new_word = input("Enter new word (press Enter to keep current): ")
                    new_answer = input("Enter new answer (press Enter to keep current): ")
                    
                    if card_manager.edit_card(
                        set_name, 
                        word,
                        new_word if new_word else None,
                        new_answer if new_answer else None
                    ):
                        print("\nCard updated successfully!")
                    else:
                        print("\nFailed to update card!")
                else:
                    print("\nInvalid card number!")
            except ValueError:
                print("\nPlease enter a valid number!")
                
        elif choice == "4":
            cards = card_manager.get_cards(set_name)
            if not cards:
                print("\nNo cards available!")
            else:
                print("\nAvailable cards:")
                for word, answer in cards.items():
                    print(f"{word} -> {answer}")
            input("\nPress Enter to continue...")
            
        elif choice == "5":
            break

def main():
    """Main application loop."""
    card_manager = CardManager()
    flashcards = Flashcards(card_manager)
    
    while True:
        # Show current set in main menu if one is selected
        current_set_info = (
            f" - Current Set: {flashcards.current_set}"
            if flashcards.current_set
            else ""
        )
        
        options = [
            "Play game",
            "Select flashcard set",
            "Manage sets",
            "Manage cards",
            "Exit"
        ]
        print_menu(f"Flashcards Menu{current_set_info}", options)
        
        choice = input("Enter your choice (1-5): ")
        
        if choice == "1":
            flashcards.game()
            input("\nPress Enter to continue...")
            
        elif choice == "2":
            sets = card_manager.get_sets()
            if not sets:
                print("\nNo sets available! Please create a set first.")
                input("\nPress Enter to continue...")
                continue
                
            print("\nAvailable sets:")
            for i, set_name in enumerate(sets, 1):
                print(f"{i}. {set_name}")
            
            try:
                idx = int(input("\nEnter set number to select: ")) - 1
                if 0 <= idx < len(sets):
                    flashcards.current_set = sets[idx]
                    print(f"\nSelected set: {sets[idx]}")
                else:
                    print("\nInvalid set number!")
            except ValueError:
                print("\nPlease enter a valid number!")
            input("\nPress Enter to continue...")
            
        elif choice == "3":
            manage_sets(card_manager)
            
        elif choice == "4":
            if not flashcards.current_set:
                print("\nPlease select a set first!")
                input("\nPress Enter to continue...")
                continue
            manage_cards(card_manager, flashcards.current_set)
            
        elif choice == "5":
            print("\nThanks for playing! Goodbye!")
            break
        
        else:
            print("\nInvalid choice! Please try again.")
            input("\nPress Enter to continue...")

if __name__ == "__main__":
    main() 