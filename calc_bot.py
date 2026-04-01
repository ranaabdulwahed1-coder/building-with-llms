import os
from dotenv import load_dotenv
from openai import OpenAI
import json
load_dotenv()
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),   # grabs key from the .env file
    base_url="https://openrouter.ai/api/v1"
)
tools = [
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
def calc(exp):
    return eval(exp)
def calc_agent():
    convo= []
    print('how can i assist you')
    while True:
        question = input('you: ')
        if question.lower() in ['quit']:
            print('adios')
            break
        convo.append({'role': 'user', 'content': question})

        response = client.chat.completions.create(
            model='stepfun/step-3.5-flash:free',
            max_tokens=1000,
            messages=convo,
            tools=tools) # needed to use tool
        choice = response.choices[0]
        if choice.finish_reason == 'tool_calls': #checks if tool is needed
            tool_call = choice.message.tool_calls[0] # gets the first tool
            arguments = json.loads(tool_call.function.arguments) # searches into the new dic that formed when tool and makes it usable
            result = calc(arguments['expression'])

            convo.append(choice.message)
            convo.append({'role': 'tool',
                         'tool_call_id' : tool_call.id,
                          'content' : str(result)
                        })
            response = client.chat.completions.create(
                model='stepfun/step-3.5-flash:free',
                max_tokens=1000,
                messages=convo,
                tools=tools)
            choice = response.choices[0]

        ai = choice.message.content
        convo.append({'role': 'assistant', 'content': ai})
        print(f'\nclaude: {ai}\n')
if __name__ == '__main__':
    calc_agent()
