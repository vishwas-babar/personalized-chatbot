from openai import OpenAI
from dotenv import load_dotenv
import os
import requests
from pprint import pprint
import json

load_dotenv(override=True)
pushover_user_key = os.getenv('PUSHOVER_USER_KEY')
pushover_token = os.getenv('PUSHOVER_TOKEN')
pushover_url = "https://api.pushover.net/1/messages.json"


def pushNotification(message):
    payload = {
        "user": pushover_user_key,
        "token": pushover_token,
        "message": message
    }
    requests.post(pushover_url, data=payload)


# pushNotification('thisi is for testing!')

def record_user_details(email, name="NA", notes="NA"):
    pushNotification(
        f"Got a request from {name} with email {email} and with notes {notes}")
    return {"recorded": True}


def record_unknown_question(question):
    pushNotification(f"recorded ques: {question}")
    return {"recorded": True}


record_user_details_json = {
    "name": "record_user_details",
    "description": "Use this tool to record that a user is interested in being in touch and provided an email address",
    "parameters": {
        "type": "object",
        "properties": {
            "email": {
                "type": "string",
                "description": "The email address of this user"
            },
            "name": {
                "type": "string",
                "description": "The user's name, if they provided it"
            },
            "notes": {
                "type": "string",
                "description": "Any additional information about the conversation that's worth recording to give context"
            }
        },
        "required": ["email"],
        "additionalProperties": False
    }
}


record_unknown_question_json = {
    "name": "record_unknown_question",
    "description": "Always use this tool to record any question that couldn't be answered as you didn't know the answer",
    "parameters": {
        "type": "object",
        "properties": {
            "question": {
                "type": "string",
                "description": "The question that couldn't be answered"
            },
        },
        "required": ["question"],
        "additionalProperties": False
    }
}


tools = [
    {"type": "function", "function": record_user_details_json},
    {"type": "function", "function": record_unknown_question_json}
]


def handle_tool_call(tool_calls): 
    results = []
    for tool in tool_calls:
        name = tool.function.name
        arguments = json.loads(tool.function.arguments)

        print(f"calling tool: {name}")

        if name == "record_user_details":
            result = record_user_details(**arguments)
        elif name == "record_unknown_question":
            result = record_unknown_question(**arguments)
       
        results.append({"role": "tool", "content": json.dumps(result), "tool_call_id": tool.id})
    return results 
        