from openai import OpenAI
from dotenv import load_dotenv
import json
from tools import get_weather, weather_tool
import os
load_dotenv()
client = OpenAI(base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY")
)
SYSTEM_PROMPT = 'you are a helpful weather assistant and your name is Claude, but you can also answer question.' \
' display the temp in both units try not to exceed one paragragh of text when responding'
messages = [{'role' : 'system', 'content': SYSTEM_PROMPT},
                 ]
def run_weather_bot(user_message):
    messages.append({"role": "user", "content": user_message})
    r = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=messages,
        tools=[weather_tool]
    )
    if r.choices[0].finish_reason != 'tool_calls':
        reply = r.choices[0].message.content
        messages.append({"role": "assistant", "content": reply})
        print(f'claude:{reply}')
        return
    tool_call = r.choices[0].message.tool_calls[0] #ai reponse
    tool_args = json.loads(tool_call.function.arguments) # data pyth can use
    result = get_weather(**tool_args) # this function gets all the necesary data from the api
        #** = dictionary unpacking, turning  ...:... to ...=...
    messages.append(r.choices[0].message)
    messages.append({
        "role": "tool",
        "tool_call_id": tool_call.id,
        "content": result
    })
    r2 = client.chat.completions.create(
        model="stepfun/step-3.5-flash:free",
        messages=messages,
        tools=[weather_tool]
    )# secocnd call
    reply = r2.choices[0].message.content #formulates response
    messages.append({"role": "assistant", "content": reply})
    print(f'\nclaude:{reply}\n')
if __name__ == "__main__":
    print("i'm claude, ask me about the weather anywhere!")
    while True:
        user_input = input("You: ")
        if user_input.lower() in ["quit", "goodbye"]:
            break

        run_weather_bot(user_input)



