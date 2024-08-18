import speech_recognition as sr
import pyttsx3
import os
import webbrowser
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import google.generativeai as genai

# Import the dictionary from websites.py
from websites import websites

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

def open_website(command):
    command = command.lower().strip()

    if command.startswith("open"):
        search_term = command.replace("open", "").strip()

        for site_name, url in websites.items():
            if site_name in search_term:
                webbrowser.open(url)
                return f"Opening {site_name.title()}."

        search_query = f"site {search_term}"
        google_search_url = f"https://www.google.com/search?q={search_query}"
        print(f"Google Search URL: {google_search_url}")

        try:
            response = requests.get(google_search_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            search_results = soup.find_all('a', href=True)
            for link in search_results:
                href = link['href']
                if "url?q=" in href:
                    first_result_url = href.split("url?q=")[1].split("&")[0]
                    print(f"Extracted URL: {first_result_url}")

                    if not any(keyword in first_result_url for keyword in ['maps.google', 'youtube.com', 'google.com']):
                        webbrowser.open(first_result_url)
                        return f"Opening {search_term.title()}."

            return f"Sorry, I couldn't find {search_term}."
        except Exception as e:
            return f"Error searching for {search_term}: {e}"
    else:
        return "Command does not start with 'open'."


if __name__ == "__main__":
    speak("Hi, I am your virtual assistant...")
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
                    if recognized_text.lower() == "hey tipu":
                        speak("Yes sir")
                        wake_word_mode = False 
                    else:
                        print("Wake word not recognized")
                else:
                    if recognized_text.lower() == "stop tipu":
                        speak("Goodbye!")
                        break 

                    if "open" in recognized_text.lower():
                        website_response = open_website(recognized_text)
                        speak(website_response)
                    else:
                        openai_response = process_command(recognized_text)
                        print(f"Response: {openai_response}")
                        speak(openai_response)

            except sr.UnknownValueError:
                print("Google did not understand the audio")
            except sr.RequestError as e:
                print(f"Google error: {e}")

        except Exception as e:
            print(f"Error during listening: {e}")
