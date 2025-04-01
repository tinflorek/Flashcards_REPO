# Flashcards

A simple command-line flashcard application written in Python for learning and memorization.

## Features

- Interactive flashcard game in the terminal
- Tracks game history and saves results to CSV
- Case-insensitive answer checking
- Ability to exit game at any time
- Randomized card order for better learning

## Usage

1. Run the application:
```bash
python main.py
```

2. The game will present you with words, and you need to provide their translations
3. Type 'exit' at any time to end the game
4. Game results will be saved automatically to `flashcard_history.csv`

## Project Structure

- `main.py` - Main application file containing the Flashcards class
- `flashcard_history.csv` - Generated file containing game history and statistics
- `requirements.txt` - Project dependencies (currently using only standard library)

## Example

The default flashcard set includes Spanish translations:
- apple → manzana
- hello → hola
- goodbye → adiós
- cat → gato
- dog → perro

You can modify the cards dictionary in `main.py` to create your own flashcard set. 