# flashcard_generator.py

import os
from openai import OpenAI
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

def generate_flashcards(text):
    client = OpenAI()
    
    # Retry logic for API calls
    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",  # Keep using gpt-4o-mini as specified
                messages=[
                    {"role": "system", "content": "You are an assistant that creates educational flashcards."},
                    {"role": "user", "content": f"Generate concise flashcards from the following text:\n\n{text}\n\nFormat each flashcard as 'Q: [Question]? A: [Answer].' Separate each flashcard with a newline."}
                ],
                max_tokens=1500,
                temperature=0.5,  # Reduced temperature for more stable outputs
                presence_penalty=0.1,
                frequency_penalty=0.1
            )
            return response.choices[0].message.content.strip().split("\n")
        except Exception as e:
            if attempt == max_retries - 1:  # Last attempt
                print(f"Error generating flashcards after {max_retries} attempts: {str(e)}")
                print("Falling back to GPT-3.5-turbo...")
                # Fallback to GPT-3.5-turbo if gpt-4o-mini fails
                response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are an assistant that creates educational flashcards."},
                        {"role": "user", "content": f"Generate concise flashcards from the following text:\n\n{text}\n\nFormat each flashcard as 'Q: [Question]? A: [Answer].' Separate each flashcard with a newline."}
                    ],
                    max_tokens=1500,
                    temperature=0.5
                )
                return response.choices[0].message.content.strip().split("\n")
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
        return False
        
    try:
        with open("flashcards.html", "w", encoding='utf-8') as file:
            html_content = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flashcards</title>
    <style>
        body { 
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .flashcard { 
            border: 1px solid #ddd;
            padding: 20px;
            margin: 10px;
            cursor: pointer;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .question { font-weight: bold; }
        .answer { 
            display: none;
            margin-top: 10px;
            color: #444;
        }
        .flashcard:hover {
            background-color: #f9f9f9;
        }
    </style>
    <script>
        function toggleAnswer(event) {
            const answer = event.currentTarget.querySelector(".answer");
            answer.style.display = answer.style.display === "block" ? "none" : "block";
        }
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
            
            file.write(html_content)
            return True
    except Exception as e:
        print(f"Error creating HTML file: {str(e)}")
        return False

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
                
                # Read all input until EOF (Ctrl+Z/Ctrl+D)
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
            
            if create_html(flashcards):
                print("Flashcards HTML file generated successfully as 'flashcards.html'.")
            else:
                print("Failed to generate flashcards HTML file.")
                
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            print("Please try again.")
            continue

if __name__ == "__main__":
    main() 