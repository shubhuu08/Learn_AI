import os
import re
import traceback
from flask import Flask, render_template, request
from groq import Groq
from gtts import gTTS

app = Flask(__name__)

# Tumchi Groq API Key
# Aadhi hoti ti kadha: client = Groq(api_key="gsk_...")

# Hich aashi replace kara:
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

@app.route("/", methods=["GET", "POST"])
def index():
    notes_desc = ""
    notes_steps = []
    audio_file = None
    topic = ""
    selected_lang = "Marathi"
    
    if request.method == "POST":
        topic = request.form.get("topic")
        selected_lang = request.form.get("language", "Marathi")
        
        if topic:
            prompt = f"""
            You are an expert educational content creator.
            A student wants to learn about the topic: '{topic}' in **{selected_lang}** language.
            
            Provide the response strictly in three sections using these exact headings:
            
            SECTION 1: DETAILED NOTES
            (Write a detailed, comprehensive, multi-paragraph educational guide explaining the topic thoroughly in {selected_lang} language. Write rich descriptive paragraphs covering definition, core concepts, and importance. Do NOT use bullet points.)
            
            SECTION 2: FLOWCHART STEPS
            (Provide exactly 4 or 5 sequential step-by-step summary points or building blocks for the topic in {selected_lang} language, each on a new line starting with a number like 1., 2., 3., etc.)
            
            SECTION 3: AUDIO SCRIPT
            (Provide a clean, natural conversational voiceover script explaining the topic in {selected_lang} language. No stage directions, no narrator labels, no intro/outro like subscribe. Only plain speech text.)
            """
            
            try:
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    model="openai/gpt-oss-20b",
                )
                full_response = chat_completion.choices[0].message.content
                
                sec1 = ""
                sec2 = ""
                sec3 = ""
                
                if "SECTION 2: FLOWCHART STEPS" in full_response and "SECTION 3: AUDIO SCRIPT" in full_response:
                    parts = full_response.split("SECTION 2: FLOWCHART STEPS")
                    sec1 = parts[0].replace("SECTION 1: DETAILED NOTES", "").strip()
                    remaining = parts[1].split("SECTION 3: AUDIO SCRIPT")
                    sec2 = remaining[0].strip()
                    sec3 = remaining[1].strip() if len(remaining) > 1 else ""
                else:
                    sec1 = full_response
                    sec2 = "1. Introduction\n2. Core Concept\n3. Conclusion"
                    sec3 = full_response
                
                notes_desc = sec1
                
                for line in sec2.split('\n'):
                    line = line.strip()
                    line_clean = re.sub(r'^[\*\-\d\.]+\s*', '', line)
                    if line_clean and not "SECTION" in line_clean and len(line_clean) > 2:
                        notes_steps.append(line_clean)
                        
                if len(notes_steps) < 3:
                    notes_steps = ["Overview", "Core Mechanism", "Key Components", "Conclusion"]
                
                clean_script = re.sub(r'[\*#_`~\-\[\]()]', ' ', sec3)
                
                lang_code_map = {
                    "Marathi": "mr",
                    "Hindi": "hi",
                    "English": "en"
                }
                tts_lang = lang_code_map.get(selected_lang, "mr")
                
                os.makedirs("static", exist_ok=True)
                audio_path = os.path.join("static", "script_audio.mp3")
                tts = gTTS(text=clean_script, lang=tts_lang, slow=False)
                tts.save(audio_path)
                audio_file = "script_audio.mp3"
                    
            except Exception as e:
                # This will print the exact error traceback in your terminal window
                print("--- ERROR OCCURRED ---")
                traceback.print_exc()
                notes_desc = f"Error generating content: {str(e)}"
                notes_steps = ["Step 1", "Step 2"]
                
    return render_template("index.html", notes_desc=notes_desc, notes_steps=notes_steps, audio_file=audio_file, topic=topic, selected_lang=selected_lang)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)