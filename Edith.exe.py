import speech_recognition as sr
import pyttsx3
import requests
import os
import subprocess
import webbrowser
import time
from deep_translator import GoogleTranslator

# ===== CONFIGURATION =====
# Replace with your actual API key (keep it secure!)
API_KEY = "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"
API_URL = "https://api.deepseek.com/v1/chat/completions"
BRAVE_PATH = os.path.join(os.environ["PROGRAMFILES"], "BraveSoftware\\Brave-Browser\\Application\\brave.exe")
DEFAULT_BROWSER = BRAVE_PATH if os.path.exists(BRAVE_PATH) else None

# ===== INITIALIZATION =====
engine = pyttsx3.init()
engine.setProperty("rate", 180)
recognizer = sr.Recognizer()
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 400

# ===== IMPROVED FUNCTIONS =====
def speak(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech error: {e}")

def listen(timeout=1.5):
    """Single-threaded listening to avoid context manager conflicts"""
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.3)
        try:
            print("🎤 Listening...")
            audio = recognizer.listen(source, timeout=timeout)
            print("🔍 Recognizing...")
            return recognizer.recognize_google(audio)
        except (sr.WaitTimeoutError, sr.UnknownValueError):
            return None
        except Exception as e:
            print(f"Listening error: {e}")
            return None

def chat_with_deepseek(prompt):
    """Improved API call with better error handling"""
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 150
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=10)
        
        # Check for API errors
        if response.status_code == 401:
            raise ValueError("Invalid API key - please check your DeepSeek API key")
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"API Error: {e}")
        return f"Sorry, I encountered an error: {str(e)}"

# ===== MAIN LOOP =====
if __name__ == "__main__":
    speak("EDITH ready. Say 'EDITH' followed by your command.")
    
    while True:
        # Wait for wake word
        print("🔍 Waiting for wake word...")
        wake_word = listen()
        
        if wake_word and "edith" in wake_word.lower():
            speak("Yes?")
            
            # Get command
            command = listen(timeout=5)  # Longer timeout for commands
            if command:
                if "exit" in command.lower() or "quit" in command.lower():
                    speak("Goodbye!")
                    break
                
                # Process command
                response = chat_with_deepseek(command)
                speak(response)
            else:
                speak("I didn't catch that.")               