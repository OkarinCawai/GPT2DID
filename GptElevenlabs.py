import os
import io
import openai
import speech_recognition as sr
from elevenlabslib import ElevenLabsUser
import requests
import sounddevice as sd
import soundfile as sf
import numpy as np
import time
from dotenv import load_dotenv
load_dotenv()
play_timeout = 10

# ELEVENLABS API KEY
api_key = os.getenv("ELEVENLABS_API_KEY")

# OPENAI API KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# Function to transcribe audio to text using Google Speech Recognition API
def transcribe_audio_to_text(filename):
    recognizer = sr.Recognizer()
    with sr.AudioFile(filename) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except:
        print('Skipping unknown error')

# Function to generate response using OpenAI's text-davinci-003 language model
def generate_response(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=4000,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response["choices"][0]["text"]

# Function to convert text to speech using ElevenLabs API
def generate_speech(text):
    url = "https://api.elevenlabs.io/v1/text-to-speech/4ilNDLaUGS8cXWGsehjE"
    headers = {"xi-api-key": api_key}
    data = {
        "text": text,
        "voice_settings": {"stability": 0, "similarity_boost": 0},
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        # Save audio data to a file
        filename = "sample.wav"
        with open(filename, "wb") as f:
            f.write(response.content)

        # Play audio using sounddevice
        with sf.SoundFile(filename) as f:
            data = f.read()
            sd.play(data, f.samplerate)
            sd.wait()
            return filename
    else:
        print("Error generating speech:", response.text)
        return None
        
def main():
    while True:
        # Wait for user to say "genius"
        print("Say 'Genius' to start recording your question...")
        with sr.Microphone(device_index=2) as source:
            recognizer = sr.Recognizer()
            audio = recognizer.listen(source)
            try:
                transcription = recognizer.recognize_google(audio)
                if transcription.lower() == "genius":
                    # Record audio
                    filename = "input.wav"
                    print("What is your question...")
                    with sr.Microphone(device_index=2) as source:
                        recognizer = sr.Recognizer()
                        source.pause_threshold = 1
                        audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
                        with open(filename, "wb") as f:
                            f.write(audio.get_wav_data())
                            
                    # Transcribe audio to text
                    text = transcribe_audio_to_text(filename)
                    if text: 
                        print(f"You said: {text}")
                        
                        # Generate response using GPT-3
                        response = generate_response(text)
                        print(f"Sarah says: {response}")
                        
                        # Convert response text to speech using ElevenLabs API
                        generate_speech(response)
            except Exception as e:
                print("Oh no! An error has occurred:", e)

if __name__ == "__main__":
    main()