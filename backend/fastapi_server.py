from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from fastapi.responses import JSONResponse
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

print("Loaded GOOGLE_API_KEY:", os.getenv("GOOGLE_API_KEY"))


app = FastAPI()

class SpeechInput(BaseModel):
    speech_text: str
    language: str

@app.post("/process_speech_input")
async def process_speech_input(speech_input: SpeechInput):
    """
    Processes speech input and generates a recipe based on the provided language.
    """
    try:
        ingredients = speech_input.speech_text
        # Language mapping for descriptive labels
        language_map = {
            "en-IN": "English",
            "te-IN": "Telugu",
            "hi-IN": "Hindi",
            "ta-IN": "Tamil",
            "kn-IN": "Kannada",
        }
        language_name = language_map.get(speech_input.language, "English")

        # Create the prompt for the generative AI
        prompt = f"""
        Create 5 recipes in {language_name} using the following ingredients provided by the user in {language_name}:
        
        Ingredients: {ingredients}
        
        Please include the following details in each recipe and details should be in {language_name}:
        1. A detailed recipe for the provided ingredients.
        2. Nutritional benefits of the ingredients used.
        3. Simple and clear cooking instructions.
        4. Suggestions for serving or enhancing the recipe.
        5. Advantages and disadvantages of the recipe.
        6. The estimated cooking time and difficulty level.

        Provide note point in {language_name}
        """

        
        # Use Google Generative AI to generate content
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        generated_recipe = response.text

        return JSONResponse(content={"recipe": generated_recipe}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@app.post("/generate_diet_plan")
async def generate_diet_plan(details: dict):
    """
    Generate a diet plan based on user-provided details.
    """
    try:
        region = details.get("region", "General")
        health_problem = details.get("health_problem", "No specific health concerns")
        food_type = details.get("food_type", "Vegetarian")
        available_vegetables = details.get("available_vegetables", "No ingredients provided")

        prompt = f"""
        Create 5 detailed and healthy recipes using the following details:
        Region: {region}
        Health Problem: {health_problem}
        Food Type: {food_type}
        Available Vegetables: {available_vegetables}

        Each recipe must include the following points:
        1. A detailed and step-by-step recipe for the provided ingredients.
        2. Nutritional benefits of the ingredients used, focusing on vitamins, minerals, and health benefits.
        3. Simple and clear cooking instructions, including preparation, cooking time, and temperature if applicable.
        4. Suggestions for serving or enhancing the recipe, including side dishes, garnishes, or modifications to suit different preferences.
        5. Advantages and disadvantages of the recipe, such as its health benefits, possible dietary restrictions, or high-calorie content if applicable.
        6. The estimated cooking time and difficulty level (easy, medium, or hard).
       """
        
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        generated_diet_plan = response.text

        return JSONResponse(content={"diet_plan": generated_diet_plan}, status_code=200)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
