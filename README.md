# Flashcard Generator

A Python application that automatically generates study flashcards from text or PDF inputs using OpenAI's API. The flashcards are generated as an interactive HTML file that can be opened in any web browser.

## Features
- Generate flashcards from text input or PDF files
- Interactive web-based flashcard interface
- Keyboard shortcuts for easy navigation
- Progress tracking
- Dark mode interface
- Automatic saving to Downloads folder

## Prerequisites
- Python 3.7 or higher
- An OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/flashcard-generator.git
cd flashcard-generator
```

2. Install the required packages:
```bash
pip install -r requirements.txt
```

3. Set up your environment:
   - Copy `.env.example` to create a new file called `.env`
   - Open `.env` and replace `your-api-key-here` with your OpenAI API key

## Usage

1. Run the application:
```bash
python flashcard_generator.py
```

2. Choose your input method:
   - Option 1: Enter text directly
     - Type or paste your text
     - Press Ctrl+Z (Windows) or Ctrl+D (Unix) and Enter when done
   - Option 2: Provide a PDF file path
     - Enter the full path to your PDF file

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

## Troubleshooting

Common Issues:
- **API Key Not Working**: Verify your API key is correctly copied into the `.env` file
- **PDF Issues**: Ensure the PDF is not password-protected or corrupted
- **HTML Not Opening**: Check your Downloads folder and open the file manually
- **Empty Response**: If no flashcards are generated, try with a shorter text input

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.