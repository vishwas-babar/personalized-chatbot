from google import genai
from dotenv import load_dotenv
import os

values = load_dotenv(override=True)

gemini_api_key = os.getenv('GEMINI_API_KEY')

if gemini_api_key:
    print(f"gemini key exist: {gemini_api_key[:8]}")
else:
    print(f"not found the gemini api key, please add it in you env file")


client = genai.Client(api_key=gemini_api_key)

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents="Please propose a hard, challenging question to assess someone's IQ. Respond only with the question."
)

print(response.text)
