# flashcard_generator.py

import os
import openai
from pdfminer.high_level import extract_text
from dotenv import load_dotenv

def generate_flashcards(text):
    response = openai.ChatCompletion.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an assistant that creates educational flashcards."},
            {"role": "user", "content": f"Generate concise flashcards from the following text:\n\n{text}\n\nFormat each flashcard as 'Q: [Question]? A: [Answer].' Separate each flashcard with a newline."}
        ],
        max_tokens=1500,
        temperature=0.7,
    )
    flashcards = response.choices[0].message['content']
    return flashcards.strip().split("\n")

def process_pdf(file_path):
    text = extract_text(file_path)
    return text

def create_html(flashcards):
    html_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Flashcards</title>
    <style>
        body { font-family: Arial, sans-serif; }
        .flashcard { border: 1px solid #ddd; padding: 20px; margin: 10px; cursor: pointer; }
        .question { font-weight: bold; }
        .answer { display: none; margin-top: 10px; }
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
    <div id="flashcards">
'''

    for flashcard in flashcards:
        if flashcard.strip() == '':
            continue
        if flashcard.startswith('Q:') and 'A:' in flashcard:
            question_part, answer_part = flashcard.split('A:', 1)
            question = question_part.replace('Q:', '').strip()
            answer = answer_part.strip()
            html_content += f'''
        <div class="flashcard" onclick="toggleAnswer(event)">
            <div class="question">{question}</div>
            <div class="answer">{answer}</div>
        </div>
'''
    html_content += '''
    </div>
</body>
</html>
'''

    with open("flashcards.html", "w", encoding='utf-8') as file:
        file.write(html_content)

def main():
    load_dotenv()
    openai.api_key = os.getenv('OPENAI_API_KEY')

    input_type = input("Enter '1' for text input or '2' to upload a PDF: ")

    if input_type == '1':
        text = input("Enter the text: ")
    elif input_type == '2':
        file_path = input("Enter the PDF file path: ")
        text = process_pdf(file_path)
    else:
        print("Invalid option.")
        return

    print("Generating flashcards... This may take a moment.")
    flashcards = generate_flashcards(text)

    create_html(flashcards)
    print("Flashcards HTML file generated as 'flashcards.html'.")

if __name__ == "__main__":
    main() 