import os

#from dotenv import load_dotenv
from google import genai

# Load environment variables
#load_dotenv()

#api_key = os.getenv("GEMINI_API_KEY")

import streamlit as st

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=api_key)


def generate_summary(prompt):

    response = client.models.generate_content(
        model="gemini-3.5-flash",   # or the model you're using
        contents=prompt
    )

    return response.text