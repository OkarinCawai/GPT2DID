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
import base64
from dotenv import load_dotenv
load_dotenv()
play_timeout = 10

# ELEVENLABS API KEY
api_key = os.getenv("ELEVENLABS_API_KEY")

# OPENAI API KEY
openai.api_key = os.getenv("OPENAI_API_KEY")

# D-ID API KEY
did_api_key = os.getenv("DID_API_KEY")

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
def generate_response(messages):
  response = openai.ChatCompletion.create(
  model="gpt-3.5-turbo",
  messages=messages
)
  return  response['choices'][0]['message']['content']

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
        return filename
    else:
        print("Error generating speech:", response.text)
        return None

# Function to send audio to D-ID API for processing
def send_audio_to_did_api(audio_file_path):
    url = "https://api.d-id.com/talks"
    
    with open(audio_file_path, "rb") as f:
        audio_data = f.read()

    payload = {
        "script": {
            "type": "audio",
            "provider": {
                "type": "microsoft",
                "voice_id": "Jenny"
            },
            "ssml": "false",
            "audio": base64.b64encode(audio_data).decode("utf-8")
        },
        "config": {
            "fluent": "false",
            "pad_audio": "0.0"
        },
        "source_url": "https://cdn.discordapp.com/attachments/1006590047987961906/1080465497197387936/okarin_portrait_of_Indian_village_man_at_a_gathering_in_the_for_3f6b864f-9f79-485f-84f5-5943c50ee152.png"
    }

    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": "Basic WVdSdGFXNUFZMkYzWVdrdVpYVTptdWJlbDlILXBtVW8zcExSTFlWWnU="
    }

    response = requests.post(url, json=payload, headers=headers)
    if response.status_code == 200:
        response_json = response.json()
        output_url = response_json.get("output", {}).get("url", "")
        if output_url.endswith(".mp4"):
            output_file_name = "output.mp4"
            with open(output_file_name, "wb") as f:
                f.write(requests.get(output_url).content)
                print(f"Video file saved to {output_file_name}")
        else:
            print("Invalid output file format:", output_url)
    else:
        print("Error generating output:", response.text)

        
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
                        audio_file_path = generate_speech(response)
                        
                        # Send audio to D-ID API for processing
                        if audio_file_path:
                            send_audio_to_did_api(audio_file_path)
            except Exception as e:
                print("Oh no! An error has occurred:", e)

if __name__ == "__main__":
    main()