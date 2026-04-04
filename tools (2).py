# what i realized is that i can store tools adn functions that i use over and over like calling my LLM and
#functions i might use in future projects here.
import json
import urllib.request
from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
def call_LLM(convo) :
    client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"),   # grabs the key
        base_url="https://openrouter.ai/api/v1")
    response = client.chat.completions.create(
            model = 'qwen/qwen3.6-plus:free',
            max_tokens = 1000,
            messages = convo,
        )
    return response.choices[0].message.content
def mod_input(message):
    convo = [{'role' : 'system',
              'content' : """you are a content moderation classifier.
your job is to analyze user messages and return only one word.

if the message contains dangerus or violent language, self harm,
or hate speech, return "unsafe".
Otherwise, return "safe".

return only "safe" or "unsafe". No other text."""}, {'role' : 'user' , 'content' : message}]
    response = call_LLM(convo)
    return response
def mod_output(message):
    convo = [{'role' : 'system', 'content' : """your job is to 2nd check the response.
              make sure the information being presented is correct and does not promote violence of any sort
              if any of those were spotted respond with only one word "unsafe"
               else write "safe". dont say anything else"""
              }, {'role' : 'user', 'content': message}]
    response = call_LLM(convo)
    return response







# pass to the 'tools' parameter in api call
weather_tool = weather_tool = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current temperature, humidity, and wind speed for a city.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g. 'Phoenix'"
                }
            },
            "required": ["location"]
        }
    }
}


def get_weather(location: str):
    geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
    with urllib.request.urlopen(geo_url) as r: #saftely gets data
        geo_data = json.loads(r.read())#converts data to enable read
# get lat and lon for url
    lat = geo_data["results"][0]["latitude"]
    lon = geo_data["results"][0]["longitude"]

    weather_url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,weathercode,windspeed_10m"
    )
    #same thing opens, reads, and converts
    with urllib.request.urlopen(weather_url) as r:
        weather_data = json.loads(r.read())
# this line gets a dictionary
    current = weather_data["current"]
#these get the specifics from the dic
    temp = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    windspeed = current["windspeed_10m"]

    return f"{location}: {temp}°C, humidity {humidity}%, wind {windspeed} km/h"

calc_tool = [
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Evaluate a math expression and return the result.",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "A math expression like '2 + 2' or '100 * 0.15'"
                    }
                },
                "required": ["expression"]
            }
        }
    }
]
def calc(expression: str):
    result = eval(expression)
    return str(result)
ALL_TOOLS=[weather_tool, calc_tool]
TOOL_FUNCTIONS = {'get_weather' : get_weather, 'calculate' : calc}
