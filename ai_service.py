import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=GEMINI_API_KEY)


def generate_meal_plan(prompt):
    response = client.models.generate_content(
        model="gemini-1.5-flash-latest",
        contents=prompt
    )

    return response.text