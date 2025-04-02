# Flashcards

A feature-rich command-line flashcard application written in Python for learning and memorization, featuring ML-based smart review scheduling.

## Features

- Interactive flashcard game in the terminal
- Multiple flashcard sets support
- Card management system (add, edit, remove cards)
- Set management (create, delete, view sets)
- Smart review scheduling with ML
- Tracks game history and saves results to CSV
- Case-insensitive answer checking
- Ability to exit game at any time
- Randomized card order for better learning

## Setup Instructions

### Option 1: Using venv (Python's built-in virtual environment)

1. Clone the repository:
```bash
git clone https://github.com/tinflorek/Flashcards_REPO.git
cd Flashcards_REPO
```

2. Create and activate virtual environment:

On Windows:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate
```

On macOS/Linux:
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run the application:
```bash
python main.py
```

### Option 2: Using Conda (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/tinflorek/Flashcards_REPO.git
cd Flashcards_REPO
```

2. Create and activate Conda environment:
```bash
# Create Conda environment with Python 3.9
conda create -n flashcards python=3.9

# Activate Conda environment
conda activate flashcards

# Install required packages
conda install numpy pandas scikit-learn joblib
```

3. Run the application:
```bash
python main.py
```

To deactivate the environment when you're done:
```bash
conda deactivate
```

## Usage

1. Main Menu Options:
   - Play game (due cards only): Review cards that are scheduled for review
   - Practice all cards: Practice with all cards regardless of schedule
   - Select flashcard set: Choose which set to use
   - Manage sets: Create, delete, or view flashcard sets
   - Manage cards: Add, remove, edit, or view cards in the current set
   - Train ML model: Manually train the review scheduling model
   - Exit: Close the application

2. Managing Sets:
   - Create new sets with optional descriptions
   - Delete existing sets
   - View all sets with their descriptions and card counts

3. Managing Cards:
   - Add new cards to the current set
   - Remove cards from the current set
   - Edit existing cards (word and/or answer)
   - View all cards in the current set with their levels and next review times

4. Smart Review System:
   - ML-based scheduling adapts to your learning patterns
   - Shows when each card is due for review
   - Automatically adjusts intervals based on performance
   - Falls back to Leitner system when insufficient data

## Project Structure

- `main.py` - Main application file with menu system and game logic
- `card_manager.py` - Card management system implementation
- `smart_review.py` - ML-based review scheduling system
- `flashcard_sets.json` - Stores all flashcard sets and their cards
- `flashcard_history.csv` - Generated file containing game history and statistics
- `requirements.txt` - Project dependencies
- `review_model.joblib` - ML model file (generated after training)

## Data Storage

- Flashcard sets and cards are stored in `flashcard_sets.json`
- Game history is saved to `flashcard_history.csv`
- ML model is saved to `review_model.joblib`
- All files are created automatically when needed

## Example Usage

1. Create a new flashcard set (e.g., "Spanish Vocabulary")
2. Add cards to your set
3. Start practicing with "Play game"
4. The system will learn from your performance
5. Use "Play game (due cards only)" for optimal review scheduling

Create different sets for different subjects:
- Language Learning (vocabulary, phrases)
- Academic Subjects (definitions, concepts)
- Test Preparation (questions, answers)
- Memory Training (any paired information) 