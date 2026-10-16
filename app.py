import os
import re
from flask import Flask, render_template, request, url_for
from groq import Groq
from gtts import gTTS

app = Flask(__name__)

# Direct Groq API key
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
            # Ekach prompt madhe notes, steps ani audio script sathi vegli information magvtoy
            single_prompt = f"""Provide detailed educational study notes, a flowchart, and a short spoken explanation script for the topic: {topic}. Language: {selected_lang}.
            Please format your response strictly using these three tags:
            [NOTES]
            Write comprehensive study details notes and example .
            [STEPS]
            Write 4 to 5 short sequential steps for a flowchart, each starting with a number (e.g., 1., 2., etc.).
            [AUDIO]
            Write a concise, engaging spoken explanation (3-4 sentences) specifically crafted to be listened to as an audio summary, written differently from the notes."""
            
            completion = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert AI tutor."},
                    {"role": "user", "content": single_prompt}
                ],
                temperature=0.7,
            )
            
            full_response = completion.choices[0].message.content
            
            # Response la [NOTES], [STEPS] ani [AUDIO] madhe split karne
            notes_desc = ""
            steps_text = ""
            audio_text = ""
            
            if "[STEPS]" in full_response and "[AUDIO]" in full_response:
                parts = full_response.split("[STEPS]")
                notes_desc = parts[0].replace("[NOTES]", "").strip()
                remaining = parts[1]
                steps_part, audio_part = remaining.split("[AUDIO]")
                steps_text = steps_part.strip()
                audio_text = audio_part.strip()
            else:
                notes_desc = full_response
                steps_text = full_response
                audio_text = full_response[:400]

            # Flowchart steps extract karne
            notes_steps = [line.strip() for line in steps_text.split('\n') if line.strip() and any(line.strip().startswith(str(i)) for i in range(1, 10))]
            if not notes_steps:
                notes_steps = [line.strip() for line in steps_text.split('\n') if line.strip()][:5]
            if not notes_steps:
                notes_steps = ["Introduction to " + topic, "Core working mechanism", "Real-world applications and summary"]

            # Audio generation using dedicated clean audio text
            os.makedirs("static", exist_ok=True)
            clean_audio_text = re.sub(r'[*#_`\-]', ' ', audio_text)
            
            tts_lang = 'mr' if selected_lang == 'Marathi' else ('hi' if selected_lang == 'Hindi' else 'en')
            tts = gTTS(text=clean_audio_text, lang=tts_lang)
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
