# Flashcards

A feature-rich command-line flashcard application written in Python for learning and memorization.

## Features

- Interactive flashcard game in the terminal
- Multiple flashcard sets support
- Card management system (add, edit, remove cards)
- Set management (create, delete, view sets)
- Tracks game history and saves results to CSV
- Case-insensitive answer checking
- Ability to exit game at any time
- Randomized card order for better learning

## Usage

1. Run the application:
```bash
python main.py
```

2. Main Menu Options:
   - Play game: Start a flashcard game with the selected set
   - Select flashcard set: Choose which set to use
   - Manage sets: Create, delete, or view flashcard sets
   - Manage cards: Add, remove, edit, or view cards in the current set
   - Exit: Close the application

3. Managing Sets:
   - Create new sets with optional descriptions
   - Delete existing sets
   - View all sets with their descriptions and card counts

4. Managing Cards:
   - Add new cards to the current set
   - Remove cards from the current set
   - Edit existing cards (word and/or answer)
   - View all cards in the current set

5. Playing the Game:
   - Select a flashcard set
   - Answer prompts for each card
   - Get immediate feedback on correct/incorrect answers
   - View final score and accuracy
   - Game results are automatically saved to `flashcard_history.csv`

## Project Structure

- `main.py` - Main application file with menu system and game logic
- `card_manager.py` - Card management system implementation
- `flashcard_sets.json` - Stores all flashcard sets and their cards
- `flashcard_history.csv` - Generated file containing game history and statistics
- `requirements.txt` - Project dependencies (currently using only standard library)

## Data Storage

- Flashcard sets and cards are stored in `flashcard_sets.json`
- Game history is saved to `flashcard_history.csv`
- Both files are created automatically when needed

## Example

Create different sets for different subjects or languages:
- Spanish Vocabulary
- French Phrases
- Math Formulas
- Programming Concepts
- Historical Dates

Each set can contain any number of cards with questions/words and their corresponding answers/translations. 