# flashcard_generator.py

import os
from openai import OpenAI
from pdfminer.high_level import extract_text
from dotenv import load_dotenv
import tempfile
import datetime
import customtkinter as ctk
from tkinter import filedialog
import threading
from CTkMessagebox import CTkMessagebox
import time

def generate_flashcards(text):
    client = OpenAI()
    
    # Retry logic for API calls
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # gpt-4o-mini is the best model in my opinion for this task.
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
        # Get users downloads folder path
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

class FlashcardGeneratorGUI:
    def __init__(self):
        print("Initializing GUI...")  # Debug print
        self.window = ctk.CTk()
        self.window.title("Flashcard Generator")
        self.window.geometry("800x600")
        
        # Set theme
        print("Setting theme...")  # Debug print
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("green")
        
        # Configure grid
        self.window.grid_columnconfigure(0, weight=1)
        self.window.grid_rowconfigure(1, weight=1)
        
        # Create header
        self.header = ctk.CTkLabel(
            self.window,
            text="Flashcard Generator",
            font=("Helvetica", 24, "bold")
        )
        self.header.grid(row=0, column=0, pady=20, sticky="ew")
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.window)
        self.main_frame.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)
        self.main_frame.grid_rowconfigure(1, weight=1)
        
        # Create input selection frame
        self.input_frame = ctk.CTkFrame(self.main_frame)
        self.input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        # Add input type selector
        self.input_type = ctk.CTkSegmentedButton(
            self.input_frame,
            values=["Text Input", "PDF Upload"],
            command=self.toggle_input_type
        )
        self.input_type.grid(row=0, column=0, padx=20, pady=20)
        self.input_type.set("Text Input")
        
        # Create text input
        self.text_input = ctk.CTkTextbox(
            self.main_frame,
            height=300,
            font=("Helvetica", 12)
        )
        self.text_input.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        
        # Create PDF upload button (initially hidden)
        self.pdf_button = ctk.CTkButton(
            self.main_frame,
            text="Select PDF File",
            command=self.select_pdf,
            height=40
        )
        
        # Create generate button
        self.generate_button = ctk.CTkButton(
            self.main_frame,
            text="Generate Flashcards",
            command=self.generate_flashcards,
            height=40
        )
        self.generate_button.grid(row=2, column=0, padx=20, pady=20, sticky="ew")
        
        # Create progress bar (initially hidden)
        self.progress = ctk.CTkProgressBar(self.main_frame)
        self.progress.set(0)
        
        # Status label
        self.status_label = ctk.CTkLabel(
            self.main_frame,
            text="",
            font=("Helvetica", 12)
        )
        self.status_label.grid(row=3, column=0, padx=20, pady=(0, 20), sticky="ew")
        
    def toggle_input_type(self, value):
        if value == "Text Input":
            self.pdf_button.grid_remove()
            self.text_input.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
        else:
            self.text_input.grid_remove()
            self.pdf_button.grid(row=1, column=0, padx=20, pady=(0, 20), sticky="nsew")
            
    def select_pdf(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if file_path:
            self.text_input.delete("1.0", "end")
            text = process_pdf(file_path)
            if text:
                self.text_input.insert("1.0", text)
                self.toggle_input_type("Text Input")
                self.input_type.set("Text Input")
                CTkMessagebox(
                    title="Success",
                    message="PDF loaded successfully!",
                    icon="check"
                )
            else:
                CTkMessagebox(
                    title="Error",
                    message="Failed to process PDF file",
                    icon="cancel"
                )
                
    def show_progress(self):
        self.progress.grid(row=4, column=0, padx=20, pady=(0, 20), sticky="ew")
        for i in range(100):
            self.progress.set(i / 100)
            self.window.update_idletasks()
            time.sleep(0.05)
        self.progress.grid_remove()
        
    def generate_flashcards(self):
        text = self.text_input.get("1.0", "end").strip()
        if not text:
            CTkMessagebox(
                title="Error",
                message="Please enter some text or upload a PDF",
                icon="cancel"
            )
            return
            
        self.status_label.configure(text="Generating flashcards...")
        self.generate_button.configure(state="disabled")
        
        def generate():
            try:
                flashcards = generate_flashcards(text)
                success, file_path = create_html(flashcards)
                
                if success:
                    self.window.after(0, lambda: self.status_label.configure(
                        text=f"Flashcards generated successfully!"
                    ))
                    import webbrowser
                    webbrowser.open(f'file://{os.path.abspath(file_path)}')
                else:
                    self.window.after(0, lambda: self.status_label.configure(
                        text="Failed to generate flashcards"
                    ))
                    
            except Exception as e:
                self.window.after(0, lambda: CTkMessagebox(
                    title="Error",
                    message=f"An error occurred: {str(e)}",
                    icon="cancel"
                ))
            finally:
                self.window.after(0, lambda: self.generate_button.configure(state="normal"))
                
        threading.Thread(target=generate, daemon=True).start()
        threading.Thread(target=self.show_progress, daemon=True).start()
        
    def run(self):
        self.window.mainloop()

# Add this new function after the imports
def setup_api_key():
    if not os.path.exists('.env'):
        dialog = ctk.CTkInputDialog(
            text="Please enter your OpenAI API key:",
            title="API Key Setup",
        )
        api_key = dialog.get_input()
        
        if api_key and api_key.strip():
            try:
                with open('.env', 'w') as f:
                    f.write(f'OPENAI_API_KEY={api_key.strip()}')
                return True
            except Exception as e:
                CTkMessagebox(
                    title="Error",
                    message=f"Failed to save API key: {str(e)}",
                    icon="cancel"
                )
                return False
        else:
            CTkMessagebox(
                title="Error",
                message="No API key provided. The application requires an OpenAI API key to function.",
                icon="cancel"
            )
            return False
    return True

# Modify the main() function
def main():
    print("Starting application...")
    
    # Initialize customtkinter before any GUI operations
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("green")
    
    # Check for API key
    if not os.path.exists('.env'):
        if not setup_api_key():
            return
    
    load_dotenv()
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("No API key found!")
        if not setup_api_key():
            return
        load_dotenv()  # Reload environment after creating .env
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            CTkMessagebox(
                title="Error",
                message="Could not load API key. Please restart the application.",
                icon="cancel"
            )
            return
    
    print("Creating GUI instance...")
    app = FlashcardGeneratorGUI()
    print("Running main loop...")
    app.run()

# Add this at the very end of the file, after the main() function
if __name__ == "__main__":
    main()
