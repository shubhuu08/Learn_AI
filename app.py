import os
from flask import Flask, render_template, request
from groq import Groq
from gtts import gTTS

app = Flask(__name__)

# Initialize Groq client safely using environment variable
GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

@app.route('/', methods=['GET', 'POST'])
def index():
    # Page pahilyanda load hotana (GET request) sagle variables empty thevnyasathi:
    notes_desc = ""
    notes_steps = ""
    audio_file = ""
    topic = ""
    selected_lang = "English"
    
    if request.method == 'POST':
        topic = request.form.get('topic', '')
        selected_lang = request.form.get('language', 'English')
        
        if topic and client:
            try:
                # Groq API call to generate notes/content
                completion = client.chat.completions.create(
                    model="llama3-8b-8192",
                    messages=[
                        {"role": "system", "content": "You are a helpful AI tutor."},
                        {"role": "user", "content": f"Provide detailed study notes and step-by-step breakdown for the topic: {topic}"}
                    ],
                    temperature=0.7,
                )
                notes_desc = completion.choices[0].message.content
                notes_steps = "Review the notes above and practice step-by-step."
                
                # Generate Audio using gTTS
                tts = gTTS(text=notes_desc[:600], lang='en') # First 600 characters for audio
                audio_path = os.path.join('static', 'output.mp3')
                os.makedirs('static', exist_ok=True)
                tts.save(audio_path)
                audio_file = 'output.mp3'
                
            except Exception as e:
                notes_desc = f"An error occurred while generating AI content: {str(e)}"
        elif not client:
            notes_desc = "Error: GROQ_API_KEY is not set in Render Environment Variables."

    return render_template(
        "index.html", 
        notes_desc=notes_desc, 
        notes_steps=notes_steps, 
        audio_file=audio_file, 
        topic=topic, 
        selected_lang=selected_lang
    )

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
