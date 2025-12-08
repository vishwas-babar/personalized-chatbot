import os
from dotenv import load_dotenv
from openai import OpenAI
from PyPDF2 import PdfReader
import gradio as gr
from pydantic import BaseModel
from pprint import pprint

class Evaluation(BaseModel):
    is_acceptable: bool
    feedback: str

load_dotenv(override=True)
gemini_key = os.getenv('GEMINI_API_KEY')

openai = OpenAI(
    api_key=gemini_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)
model_name = "gemini-2.5-flash"

reader = PdfReader("src/me/profile.pdf")
linkedin = ''
for page in reader.pages:
    text = page.extract_text()
    if text:
        linkedin += text


with open('src/me/summary.txt', 'r', encoding="utf-8") as f:
    summary = f.read()

name = 'vishwas babar'

system_prompt = f"You are acting as {name}. You are answering questions on {name}'s website, \
particularly questions related to {name}'s career, background, skills and experience. \
Your responsibility is to represent {name} for interactions on the website as faithfully as possible. \
You are given a summary of {name}'s background and LinkedIn profile which you can use to answer questions. \
Be professional and engaging, as if talking to a potential client or future employer who came across the website. \
If you don't know the answer, say so."

system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
system_prompt += f"With this context, please chat with the user, always staying in character as {name}."


evaluator_system_prompt = f"You are an evaluator that decides whether a response to a question is acceptable. \
You are provided with a conversation between a User and an Agent. Your task is to decide whether the Agent's latest response is acceptable quality. \
The Agent is playing the role of {name} and is representing {name} on their website. \
The Agent has been instructed to be professional and engaging, as if talking to a potential client or future employer who came across the website. \
The Agent has been provided with context on {name} in the form of their summary and LinkedIn details. Here's the information:"

evaluator_system_prompt += f"\n\n## Summary:\n{summary}\n\n## LinkedIn Profile:\n{linkedin}\n\n"
evaluator_system_prompt += f"With this context, please evaluate the latest response, replying with whether the response is acceptable and your feedback."


def evaluator_user_prompt(reply, message, history):
    user_prompt = f"Here's the conversation between the User and the Agent: \n\n{history}\n\n"
    user_prompt += f"Here's the latest message from the User: \n\n{message}\n\n"
    user_prompt += f"Here's the latest response from the Agent: \n\n{reply}\n\n"
    user_prompt += "Please evaluate the response, replying with whether it is acceptable and your feedback."
    return user_prompt


def evaluate(reply, message, history) -> Evaluation:

    messages = [
        {
            "role": "system",
            "content": evaluator_system_prompt
        },
        {
            "role": "user",
            "content": evaluator_user_prompt(reply, message, history)
        }
    ]

    response = openai.chat.completions.parse(
        model=model_name, messages=messages, response_format=Evaluation)

    # pprint(response.model_dump())
    return response.choices[0].message.parsed


def rerun(reply, message, history, feedback):
    updated_system_prompt = system_prompt + \
        "\n\n## Previous answer rejected\nYou just tried to reply, but the quality control rejected your reply\n"
    updated_system_prompt += f"## Your attempted answer:\n{reply}\n\n"
    updated_system_prompt += f"## Reason for rejection:\n{feedback}\n\n"
    messages = [
        {
            "role": "system",
            "content": updated_system_prompt
        },
        *history,
        {
            "role": "user",
            "content": message
        }
    ]
    # reattempt
    response = openai.chat.completions.create(
        model=model_name, messages=messages)
    return response.choices[0].message.content




def chat(message, history):

    messages = [{
        "role": "system",
        "content": system_prompt
    }] + history + [{
        "role": "user",
        "content": message
    }]

    res = openai.chat.completions.create(model=model_name, messages=messages)
    firstReply = res.choices[0].message.content

    attemtCount = 1
    check_passed = False
    # evaluate the reply of ai
    while not check_passed:
        print(f"attempt {attemtCount} for message: {message}")
        evaluation = evaluate(firstReply, message, history)
        if evaluation.is_acceptable:
            check_passed = True
        else:
            firstReply = rerun(firstReply, message,
                               history, evaluation.feedback)

    return firstReply


gr.ChatInterface(chat).launch()


# testQuestion = "please give me the apples"
# testResponse = openai.chat.completions.create(
#     model=model_name, messages=[{"role": "user", "content": testQuestion}])
# testReply = testResponse.choices[0].message.content

# evaluationResult = evaluate(testReply, testQuestion, [{"role": "user", "content": testQuestion}])
# print("following is the eval response: ")
# pprint( evaluationResult.model_dump())
