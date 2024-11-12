# flashcard_generator.py

import os
from openai import OpenAI
from pdfminer.high_level import extract_text
from dotenv import load_dotenv
import tempfile
import datetime

def generate_flashcards(text):
    client = OpenAI()
    
    # Retry logic for API calls
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # gpt-4o-mini is the best model in my opinion.
                messages=[
                    {"role": "system", "content": "You are an assistant that creates educational flashcards. Create 5-30 (as many as deemed fit) concise question-answer pairs from the provided text."},
                    {"role": "user", "content": f"Create flashcards from this text. Each flashcard should have a clear question and answer:\n\n{text}\n\nFormat EXACTLY as:\nQ: [Question]?\nA: [Answer]\n"}
                ],
                max_tokens=1500,
                temperature=0.5,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            # Add more detailed error logging
            if not response or not response.choices:
                raise ValueError("Empty response received from OpenAI API")
                
            content = response.choices[0].message.content.strip()
            if not content:
                raise ValueError("Empty content received from OpenAI API")
                
            # Process the response to ensure proper formatting
            flashcards = []
            
            # Split into individual flashcards and validate format
            cards = content.split('\n\n')
            for card in cards:
                lines = card.strip().split('\n')
                if len(lines) >= 2 and lines[0].startswith('Q:') and any(l.startswith('A:') for l in lines[1:]):
                    flashcards.append(card.strip())
            
            # If no valid flashcards were found, raise an exception to trigger fallback
            if not flashcards:
                raise ValueError("No valid flashcards generated")
                
            return flashcards
            
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"Error generating flashcards after {max_retries} attempts:")
                print(f"Error type: {type(e).__name__}")
                print(f"Error details: {str(e)}")
                print("Falling back to GPT-3.5-turbo...")
                try:
                    # Fallback to GPT-3.5-turbo with more explicit instructions
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an assistant that creates educational flashcards. Create 5-30 (as many as deemed fit) concise question-answer pairs from the provided text."},
                            {"role": "user", "content": f"Create flashcards from this text. Each flashcard should have a clear question and answer:\n\n{text}\n\nFormat EXACTLY as:\nQ: [Question]?\nA: [Answer]\n"}
                        ],
                        max_tokens=1500,
                        temperature=0.5
                    )
                    
                    content = response.choices[0].message.content.strip()
                    flashcards = []
                    
                    cards = content.split('\n\n')
                    for card in cards:
                        lines = card.strip().split('\n')
                        if len(lines) >= 2 and lines[0].startswith('Q:') and any(l.startswith('A:') for l in lines[1:]):
                            flashcards.append(card.strip())
                    
                    if not flashcards:
                        raise ValueError("No valid flashcards generated")
                        
                    return flashcards
                    
                except Exception as e2:
                    print(f"Fallback also failed: {str(e2)}")
                    # Return a test flashcard to help debug the HTML generation
                    return [
                        "Q: What is the main topic of the text?\nA: This is a test answer to verify HTML generation.",
                        "Q: Is the flashcard system working?\nA: This is a second test card to check formatting."
                    ]
            print(f"Attempt {attempt + 1} failed, retrying...")
            continue

def process_pdf(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
            
        text = extract_text(file_path)
        if not text or not text.strip():
            raise ValueError("No text could be extracted from the PDF. The file might be empty, corrupted, or password-protected.")
        return text
    except Exception as e:
        print(f"Error processing PDF: {type(e).__name__}: {str(e)}")
        return None

def create_html(flashcards):
    if not flashcards:
        print("Debug: No flashcards received")
        return False, None
        
    print(f"Debug: Received {len(flashcards)} flashcards")
    for i, card in enumerate(flashcards):
        print(f"Debug: Card {i+1}: {card[:100]}...")

    # Create the HTML content with improved styling
    html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flashcards</title>
    <style>
        body { 
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            background-color: #1a1a1a;
            color: #fff;
            min-height: 100vh;
            line-height: 1.6;
            display: flex;
            flex-direction: column;
            align-items: center;
        }
        h1 {
            text-align: center;
            color: #fff;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 10px rgba(255,255,255,0.1);
        }
        #flashcards {
            position: relative;
            width: 100%;
            height: 60vh;
            min-height: 400px;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .flashcard { 
            position: absolute;
            width: 90%;
            max-width: 600px;
            min-height: 300px;
            background: linear-gradient(145deg, #2d2d2d, #2a2a2a);
            border: 1px solid #3d3d3d;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            padding: 40px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            cursor: pointer;
            transition: transform 0.6s;
            transform-style: preserve-3d;
            opacity: 0;
            visibility: hidden;
        }
        .flashcard.active {
            opacity: 1;
            visibility: visible;
        }
        .flashcard.flipped {
            transform: rotateX(180deg);
        }
        .question, .answer { 
            backface-visibility: hidden;
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 40px;
            text-align: center;
        }
        .question {
            font-weight: 600;
            font-size: 1.8em;
            color: #fff;
            transform: rotateX(0deg);
        }
        .answer { 
            color: #d4d4d4;
            font-size: 1.4em;
            letter-spacing: 0.2px;
            transform: rotateX(180deg);
            border-top: none;
        }
        #progress-bar {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 4px;
            background: #333;
            z-index: 1000;
        }
        #progress-fill {
            height: 100%;
            width: 0%;
            background: linear-gradient(90deg, #4CAF50, #8BC34A);
            transition: width 0.3s ease;
        }
        #card-counter {
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(45, 45, 45, 0.9);
            padding: 8px 16px;
            border-radius: 8px;
            font-size: 1.1em;
            z-index: 1000;
        }
        .navigation {
            margin-top: 20px;
            display: flex;
            gap: 20px;
            z-index: 1000;
        }
        .navigation button {
            padding: 12px 24px;
            font-size: 1.1em;
            border: none;
            border-radius: 8px;
            background: #4CAF50;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 2px 8px rgba(0,0,0,0.2);
        }
        .navigation button:hover:not(:disabled) {
            background: #45a049;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }
        .navigation button:disabled {
            background: #666;
            cursor: not-allowed;
            opacity: 0.5;
        }
        #shortcuts-info {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: rgba(45, 45, 45, 0.9);
            padding: 10px 15px;
            border-radius: 8px;
            font-size: 0.8em;
            color: #aaa;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const cards = document.querySelectorAll('.flashcard');
            let currentCard = 0;

            function showCard(index) {
                cards.forEach((card, i) => {
                    card.classList.remove('active');
                    if (i === index) {
                        card.classList.add('active');
                    }
                });
                updateNavButtons();
                updateProgress();
            }

            window.nextCard = function() {
                if (currentCard < cards.length - 1) {
                    currentCard++;
                    showCard(currentCard);
                }
            }

            window.previousCard = function() {
                if (currentCard > 0) {
                    currentCard--;
                    showCard(currentCard);
                }
            }

            function updateNavButtons() {
                document.getElementById('prevBtn').disabled = currentCard === 0;
                document.getElementById('nextBtn').disabled = currentCard === cards.length - 1;
            }

            function updateProgress() {
                const progress = ((currentCard + 1) / cards.length) * 100;
                document.getElementById('progress-fill').style.width = progress + '%';
                document.getElementById('card-counter').textContent = `Card ${currentCard + 1} of ${cards.length}`;
            }

            document.addEventListener('keydown', (e) => {
                if (e.code === 'ArrowLeft' && currentCard > 0) {
                    previousCard();
                }
                if (e.code === 'ArrowRight' && currentCard < cards.length - 1) {
                    nextCard();
                }
                if (e.code === 'Space') {
                    e.preventDefault();
                    toggleAnswer({ currentTarget: cards[currentCard] });
                }
            });

            window.toggleAnswer = function(event) {
                const card = event.currentTarget;
                card.classList.toggle('flipped');
            }

            // Initialize
            showCard(0);
        });
    </script>
</head>
<body>
    <div id="progress-bar">
        <div id="progress-fill"></div>
    </div>
    <div id="card-counter"></div>
    <div id="flashcards">'''

    for flashcard in flashcards:
        if flashcard.strip() and 'Q:' in flashcard and 'A:' in flashcard:
            try:
                question_part, answer_part = flashcard.split('A:', 1)
                question = question_part.replace('Q:', '').strip()
                answer = answer_part.strip()
                
                html_content += f'''
        <div class="flashcard" onclick="toggleAnswer(event)">
            <div class="question">{question}</div>
            <div class="answer">{answer}</div>
        </div>'''
            except Exception as e:
                print(f"Skipping malformed flashcard: {flashcard}")
                continue

    html_content += '''
    </div>
    <div class="navigation">
        <button id="prevBtn" onclick="previousCard()">← Previous</button>
        <button id="nextBtn" onclick="nextCard()">Next →</button>
    </div>
    <div id="shortcuts-info">
        Shortcuts: ← Previous | → Next | Space Toggle
    </div>
</body>
</html>'''

    try:
        # Get downloads folder path
        downloads_path = os.path.join(os.path.expanduser('~'), 'Downloads')
        
        # Generate unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"flashcards_{timestamp}.html"
        output_file = os.path.join(downloads_path, filename)
        
        # Normalize the path to use correct system separators
        output_file = os.path.normpath(output_file)
        
        with open(output_file, "w", encoding='utf-8') as file:
            file.write(html_content)
        print(f"\nSuccessfully wrote file to Downloads folder: {output_file}")
        return True, output_file
        
    except Exception as e:
        print(f"\nFailed to write file: {str(e)}")
        return False, None

def main():
    load_dotenv()
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("Error: OPENAI_API_KEY not found in environment variables")
        print("Please add your OpenAI API key to the .env file")
        return

    while True:
        try:
            print("\nFlashcard Generator")
            print("-" * 20)
            print("1: Enter text input")
            print("2: Upload a PDF")
            print("q: Quit")
            input_type = input("\nChoose an option (1/2/q): ").strip().lower()
            
            if input_type == 'q':
                print("\nThank you for using Flashcard Generator!")
                break

            if input_type not in ['1', '2']:
                print("Invalid option. Please enter 1, 2, or q.")
                continue

            text = None
            if input_type == '1':
                print("\nEnter or paste your text below.")
                print("(Press Ctrl+Z on Windows or Ctrl+D on Unix and then Enter to finish)")
                print("-" * 50)
                
                contents = []
                try:
                    while True:
                        line = input()
                        contents.append(line)
                except EOFError:
                    text = '\n'.join(contents).strip()
                except KeyboardInterrupt:
                    print("\nInput cancelled.")
                    continue
                
                if not text:
                    print("Error: Empty text input")
                    continue
            else:
                file_path = input("Enter the PDF file path: ").strip()
                if not os.path.exists(file_path):
                    print("Error: File not found")
                    continue
                text = process_pdf(file_path)
                if not text:
                    continue

            print("\nGenerating flashcards... This may take a moment.")
            flashcards = generate_flashcards(text)
            
            success, file_path = create_html(flashcards)
            if success:
                print(f"\nFlashcards HTML file generated successfully at: {file_path}")
                # Try to open the file in the default browser
                try:
                    import webbrowser
                    webbrowser.open(f'file://{os.path.abspath(file_path)}')
                except Exception as e:
                    print(f"Note: Could not automatically open the file: {str(e)}")
            else:
                print("Failed to generate flashcards HTML file.")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.")
            continue

if __name__ == "__main__":
    main() 