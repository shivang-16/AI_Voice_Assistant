import speech_recognition as sr
import pyttsx3
import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

engine = pyttsx3.init()  

def speak(text):
    engine.say(text)
    engine.runAndWait()

def process_command(command):
    try:
        response = model.generate_content(command)
        text_content = response._result.candidates[0].content.parts[0].text
        return text_content
    except Exception as e:
        return f"Error processing command with Generative AI: {e}"

if __name__ == "__main__":
    speak("Hi I am your virtual assistant...")
    wake_word_mode = True

    r = sr.Recognizer()

    while True:
        try:
            with sr.Microphone() as source:
                if wake_word_mode:
                    print("Listening for wake word...")
                else:
                    print("Listening for command...")

                audio = r.listen(source, timeout=10, phrase_time_limit=5)
                print("Audio captured")

            try:
                recognized_text = r.recognize_google(audio)
                print(f"Recognized text: {recognized_text}")

                if wake_word_mode:
                    if recognized_text.lower() == "tipu":
                        speak("Yes sir")
                        wake_word_mode = False 
                    else:
                        print("Wake word not recognized")
                else:
                    if recognized_text.lower() == "stop tipu":
                        speak("Goodbye!")
                        break 

                    # Process command with Generative AI
                    openai_response = process_command(recognized_text)
                    print(f"Response: {openai_response}")
                    speak(openai_response)

            except sr.UnknownValueError:
                print("Google did not understand the audio")
            except sr.RequestError as e:
                print(f"Google error: {e}")

        except Exception as e:
            print(f"Error during listening: {e}")
