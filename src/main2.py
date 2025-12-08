import os
import json
from dotenv import load_dotenv
from google import genai
from IPython.display import Markdown, display
from openai import OpenAI


load_dotenv(override=True)

gemini_key = os.getenv('GEMINI_API_KEY')

if gemini_key:
    print(f"gemini key exist: {gemini_key[0:6]}")
else:
    print('gemini key not found in env')


# google sdk
# client = genai.Client()

# res = client.models.generate_content(
#     model='gemini-2.5-flash',
#     contents='how python works internally?'
# )

# print(f'{res.text}')
# display(Markdown(res.text))


messages = [
    {"role": "user", "content": "Plan a 3-day trip to Goa."},
    {"role": "assistant", "content": "Here’s a sample itinerary…"},
    {"role": "user", "content": "Add budget and travel details."},
    {"role": "assistant", "content": "Budget breakdown…"},
    {"role": "user", "content": "Now give me the final summary."}
]


# openai sdk
client = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model_name = 'gemini-2.5-flash'

response = client.chat.completions.create(model=model_name, messages=messages)
answer = response.choices[0].message.content

print(answer)
display(Markdown(answer))
