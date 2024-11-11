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
                    {"role": "system", "content": "You are an assistant that creates educational flashcards. Create 5-40 (as many as deemed fit) concise question-answer pairs from the provided text."},
                    {"role": "user", "content": f"Create flashcards from this text. Each flashcard should have a clear question and answer:\n\n{text}\n\nFormat EXACTLY as:\nQ: [Question]?\nA: [Answer]\n"}
                ],
                max_tokens=1500,
                temperature=0.5,
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            
            # Process the response to ensure proper formatting
            content = response.choices[0].message.content.strip()
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
                print(f"Error generating flashcards after {max_retries} attempts: {str(e)}")
                print("Falling back to GPT-3.5-turbo...")
                try:
                    # Fallback to GPT-3.5-turbo with more explicit instructions
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are an assistant that creates educational flashcards. Create 5-10 concise question-answer pairs from the provided text."},
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
        text = extract_text(file_path)
        if not text.strip():
            raise ValueError("No text could be extracted from the PDF")
        return text
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")
        return None

def create_html(flashcards):
    if not flashcards:
        print("Debug: No flashcards received")
        return False, None
        
    print(f"Debug: Received {len(flashcards)} flashcards")
    for i, card in enumerate(flashcards):
        print(f"Debug: Card {i+1}: {card[:100]}...")  # Print first 100 chars of each card

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
        }
        h1 {
            text-align: center;
            color: #fff;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 0 0 10px rgba(255,255,255,0.1);
        }
        .flashcard { 
            background-color: #2d2d2d;
            border: 1px solid #3d3d3d;
            padding: 30px;
            margin: 20px auto;
            cursor: pointer;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            max-width: 600px;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            position: relative;
            overflow: hidden;
        }
        .flashcard:hover {
            transform: translateY(-5px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            background-color: #333333;
        }
        .flashcard:active {
            transform: translateY(0) scale(0.98);
        }
        .question { 
            font-weight: 600;
            font-size: 1.3em;
            color: #fff;
            text-align: center;
            margin-bottom: 15px;
            line-height: 1.4;
        }
        .answer { 
            display: none;
            margin-top: 20px;
            color: #b3b3b3;
            text-align: center;
            padding-top: 15px;
            border-top: 1px solid #3d3d3d;
            line-height: 1.5;
            animation: fadeIn 0.5s ease-in-out;
        }
        .flashcard::after {
            content: "Click to reveal answer";
            position: absolute;
            bottom: 10px;
            left: 50%;
            transform: translateX(-50%);
            font-size: 0.8em;
            color: #666;
            opacity: 0.7;
            transition: opacity 0.3s ease;
        }
        .flashcard:hover::after {
            opacity: 1;
            color: #888;
        }
        .flashcard.show-answer::after {
            content: "Click to hide answer";
        }
        @keyframes fadeIn {
            from {
                opacity: 0;
                transform: translateY(10px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateX(-20px);
            }
            to {
                opacity: 1;
                transform: translateX(0);
            }
        }
        .flashcard {
            animation: slideIn 0.5s ease-out;
            animation-fill-mode: both;
        }
        .flashcard:nth-child(1) { animation-delay: 0.1s; }
        .flashcard:nth-child(2) { animation-delay: 0.2s; }
        .flashcard:nth-child(3) { animation-delay: 0.3s; }
        .flashcard:nth-child(4) { animation-delay: 0.4s; }
        .flashcard:nth-child(5) { animation-delay: 0.5s; }
        
        /* Glowing effect on hover */
        .flashcard:hover {
            box-shadow: 0 8px 25px rgba(0,0,0,0.3),
                        0 0 20px rgba(255,255,255,0.05),
                        0 0 40px rgba(255,255,255,0.02);
        }
        
        /* Smooth transition for answer reveal */
        .answer {
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        @media (max-width: 600px) {
            body {
                padding: 15px;
            }
            .flashcard {
                padding: 20px;
                margin: 15px auto;
            }
            h1 {
                font-size: 2em;
            }
        }
        
        /* Selection color */
        ::selection {
            background: #404040;
            color: #fff;
        }
    </style>
    <script>
        function toggleAnswer(event) {
            const card = event.currentTarget;
            const answer = card.querySelector(".answer");
            const isHiding = answer.style.display === "block";
            
            answer.style.opacity = "0";
            answer.style.transform = "translateY(10px)";
            
            if (!isHiding) {
                answer.style.display = "block";
                setTimeout(() => {
                    answer.style.opacity = "1";
                    answer.style.transform = "translateY(0)";
                }, 10);
                card.classList.add("show-answer");
            } else {
                setTimeout(() => {
                    answer.style.display = "none";
                }, 300);
                card.classList.remove("show-answer");
            }
        }
        
        // Add entrance animations when page loads
        document.addEventListener("DOMContentLoaded", function() {
            const cards = document.querySelectorAll(".flashcard");
            cards.forEach((card, index) => {
                card.style.animationDelay = `${index * 0.1}s`;
            });
        });
    </script>
</head>
<body>
    <h1>Generated Flashcards</h1>
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
    
    if not os.getenv('OPENAI_API_KEY'):
        print("Error: OPENAI_API_KEY not found in environment variables")
        return

    while True:
        try:
            print("\nOptions:")
            print("1: Enter text input")
            print("2: Upload a PDF")
            print("q: Quit")
            input_type = input("Choose an option (1/2/q): ").strip().lower()
            
            if input_type == 'q':
                print("Goodbye!")
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