import streamlit as st
import requests
import speech_recognition as sr
from googletrans import Translator
from typing import Dict, Tuple

def verify_language_support(language_code: str) -> bool:
    """Verify if the language is supported by the application."""
    supported_languages = {
        "en-IN": "English",
        "te-IN": "Telugu",
        "hi-IN": "Hindi",
        "ta-IN": "Tamil",
        "kn-IN": "Kannada",
    }
    return language_code in supported_languages

def initialize_translator() -> Translator:
    """Initialize the translator with fallback URLs."""
    try:
        return Translator(service_urls=['translate.google.com'])
    except Exception as e:
        st.error("Translation service initialization failed")
        raise

def process_speech_input(recognizer: sr.Recognizer, audio_data: sr.AudioData, 
                        language: Tuple[str, str], translator: Translator) -> str:
    """Process speech input and return translated text."""
    try:
        speech_text = recognizer.recognize_google(audio_data, language=language[1])
        st.success(f"You said (in {language[0]}): {speech_text}")
        return speech_text
    except sr.UnknownValueError:
        raise ValueError("Could not understand audio. Please try speaking clearly.")
    except sr.RequestError as e:
        raise

def main():
    st.title("Recipe Hub")
    st.write("Provide your details or use voice input to get a customized recipe plan.")

    st.subheader("Speak Your Details")
    st.info("Select your preferred language and click the button below to speak your details.")

    language = st.selectbox(
        "Select Language for Speech Recognition",
        options=[
            ("English","en-IN"),
            ("Telugu", "te-IN"),
            ("Hindi", "hi-IN"),
            ("Tamil", "ta-IN"),
            ("Kannada", "kn-IN"),
        ],
        format_func=lambda x: x[0]
    )

    try:
        translator = initialize_translator()
    except Exception:
        st.error("Failed to initialize translation service. Please try again later.")
        return

    if st.button("Start Speaking"):
        if not verify_language_support(language[1]):
            st.error(f"Language {language[0]} is not fully supported")
            return

        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            st.info("Listening... Speak now.")
            try:
                recognizer.adjust_for_ambient_noise(source)
                audio_data = recognizer.listen(source, timeout=15, phrase_time_limit=10)
                translated_text = process_speech_input(recognizer, audio_data, language, translator)

                payload = {"speech_text": translated_text, "language": language[1]}
                api_url = "http://127.0.0.1:8001/process_speech_input"
                
                response = requests.post(api_url, json=payload, timeout=30)
                
                if response.status_code == 200:
                    recipe = response.json().get("recipe", "No response text received.")
                    st.markdown(f"### Your Personalized Recipe\n\n{recipe}", unsafe_allow_html=True)
                else:
                    error_detail = response.json().get("detail", "No error detail provided.")
                    st.error(f"Error: {response.status_code} - {error_detail}")
            
            except ValueError as ve:
                st.error(str(ve))
            except Exception as e:
                st.error(f"Error processing speech input: {str(e)}")

    # Manual input form
    st.subheader("Enter Your Details Manually")
    region = st.selectbox(
        "Region", 
        ["Andra Pradesh India", "Telengana India", "Karnataka India", 
         "Tamil Naidu India", "Goa India", "Uttar Pradesh India", "International"]
    )
    health_problem = st.text_input("Health Problem")
    food_type = st.selectbox("Food Type", ["Vegetarian", "Vegan", "Non-Vegetarian"])
    available_vegetables = st.text_area("Available Vegetables", " ")

    if st.button("Generate Recipe 🐼🍴✨"):
        payload = {
            "region": region,
            "health_problem": health_problem,
            "food_type": food_type,
            "available_vegetables": available_vegetables
        }

        try:
            api_url = "http://127.0.0.1:8001/generate_diet_plan"
            response = requests.post(api_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                diet_plan = response.json().get("diet_plan", "No response text received.")
                st.markdown(f"### Your Personalized Diet Plan\n\n{diet_plan}", unsafe_allow_html=True)
            else:
                error_detail = response.json().get("detail", "No error detail provided.")
                st.error(f"Error: {response.status_code} - {error_detail}")
        
        except requests.exceptions.Timeout:
            st.error("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            st.error(f"Error connecting to the server: {str(e)}")

if __name__ == "__main__":
    main()
