# Flashcard Generator

A Python application that automatically generates study flashcards from text or PDF inputs using OpenAI's API. The flashcards are generated as an interactive HTML file that can be opened in any web browser.

## Features
- Generate flashcards from text input or PDF files
- Interactive web-based flashcard interface
- Keyboard shortcuts for easy navigation
- Progress tracking
- Dark mode interface
- Automatic saving to Downloads folder

## Installation Options

### Option 1: Download the Executable (Windows)
1. Download the [flashcard_generator_exe.zip](https://github.com/yohoxxz/flashcard-generator/releases/latest/download/flashcard_generator_exe.zip)
2. Extract the zip file
3. Run `flashcard_generator.exe`
4. On first run, you'll need to enter your OpenAI API key

### Option 2: Run from Source

#### Prerequisites
- Python 3.7 or higher
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

#### Setup Steps
1. Clone the repository:
```bash
git clone https://github.com/yohoxxz/flashcard-generator.git
cd flashcard-generator
```

2. Navigate to the Python directory:
```bash
cd flashcard_generator_py
```

3. Create a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install the required packages:
```bash
pip install -r requirements.txt
```

5. Run the application (you will enter you api key on first run):
```bash
python flashcard_generator.py
```

## Usage

1. Start the application (either the exe or Python script)

2. Choose your input method:
   - Option 1: Paste Text
   - Option 2: PDF
  

3. The program will:
   - Generate flashcards using OpenAI's API
   - Create an HTML file in your Downloads folder
   - Automatically open the flashcards in your default browser

## Using the Flashcards

Navigation:
- Click on a card or press SPACE to flip between question and answer
- Use arrow keys (← →) or buttons to navigate between cards
- Progress bar shows your position in the deck
- Card counter displays current card number

Keyboard Shortcuts:
- SPACE: Flip card
- →: Next card
- ←: Previous card

## Project Structure
```
flashcard-generator/
├── flashcard_generator_exe.zip     # Windows executable
└── flashcard_generator_py/         # Python source code
    ├── flashcard_generator.py      # Main application
    └── requirements.txt            # Python dependencies
```

## Troubleshooting

Common Issues:
- **API Key Not Working**: Verify your API key is correctly entered
- **PDF Issues**: Make sure the PDF is not password-protected or corrupted
- **HTML Not Opening**: Check your Downloads folder and open the file manually
- **Empty Response**: If no flashcards are generated, try with a shorter text input
- **Exe Not Running**: Make sure you've extracted all files from the zip folder
- **Module Not Found**: Ensure you're in the correct directory and requirements.txt is installed

## Contributing

Contributions are welcome! Im just a HS student that has no clue what hes doing. Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
