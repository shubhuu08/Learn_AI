import os
from flask import Flask, render_template, request, url_for
from groq import Groq
from gtts import gTTS

app = Flask(__name__)

# Direct Groq API key (kiwa environment variable)
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

@app.route("/", methods=["GET", "POST"])
def index():
    notes_desc = ""
    notes_steps = []
    selected_lang = "English"
    topic = ""
    audio_file = ""
    
    if request.method == "POST":
        topic = request.form.get("topic")
        selected_lang = request.form.get("language", "English")
        
        try:
            # Groq API call to get detailed notes and steps
            prompt = f"Provide detailed educational notes and a step-by-step breakdown (at least 3-4 steps) for the topic: {topic}. Language: {selected_lang}. Format it clearly with paragraphs for summary and numbered steps for the breakdown."
            
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert AI tutor."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
            )
            
            full_response = completion.choices[0].message.content
            notes_desc = full_response
            
            # Simple splitting for flowchart steps (dividing by newlines or bullet points)
            lines = [line.strip() for line in full_response.split('\n') if line.strip()]
            notes_steps = [line for line in lines if line.startswith(('1.', '2.', '3.', '4.', '5.', '-', '*'))][:5]
            if not notes_steps:
                notes_steps = ["Introduction and core concept of " + topic, "Working mechanism and architecture", "Real-world applications and summary"]

            # Generate Audio using gTTS
            os.makedirs("static", exist_ok=True)  # He ohl add kara (folder nsel tar banvel)
            tts_lang = 'mr' if selected_lang == 'Marathi' else ('hi' if selected_lang == 'Hindi' else 'en')
            tts = gTTS(text=full_response[:600], lang=tts_lang)
            audio_filename = "script_audio.mp3"
            audio_path = os.path.join("static", audio_filename)
            tts.save(audio_path)
            audio_file = audio_filename
            
        except Exception as e:
            notes_desc = f"An error occurred while generating AI content: {str(e)}"
            notes_steps = ["Error occurred during step generation."]
                
    return render_template("index.html", notes_desc=notes_desc, notes_steps=notes_steps, selected_lang=selected_lang, topic=topic, audio_file=audio_file)

if __name__ == "__main__":
    app.run(debug=True)
