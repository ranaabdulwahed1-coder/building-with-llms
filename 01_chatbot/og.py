from openai import OpenAI        # loads libary
from dotenv import load_dotenv   # allows to read the file
import os                   # accessing system stuff
from tools import mod_output

load_dotenv()                    # reads the .env file
client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),   # grabs key from the .env file
    base_url="https://openrouter.ai/api/v1"
)
def moderate_input(message):
    response = client.chat.completions.create(
        model='stepfun/step-3.5-flash:free',
        messages=[
            {
                "role": "system",
                "content": """You are a content moderation classifier.
Your job is to analyze user messages and return only one word.

If the message contains dangerous or violent language, self-harm,
or hate speech, return "unsafe".
Otherwise, return "safe".

Return only "safe" or "unsafe". No other text."""
            },
            {
                "role": "user",
                "content": message
            }])
    return response.choices[0].message.content.strip().lower()
def chat():
    convo = []
    print(' What is on your mind(type quit or goodbye to end chat)\n')
    while True:
        user_input = input('you: ')
        if moderate_input(user_input) == "unsafe":
            print("Assistant: I can't help with that.")
            continue
        if user_input.lower() in ['quit', 'goodbye']:
            print(' adios brochacho')
            break
        convo.append({'role' : 'user', 'content' : user_input})
        response = client.chat.completions.create(
            model = 'stepfun/step-3.5-flash:free',
            max_tokens = 1000,
            messages = convo,
        )
        ai_talk = response.choices[0].message.content
        if mod_output(ai_talk) == "safe":
            convo.append({'role' : 'assistant', 'content' : ai_talk})
            print(f'Claude: {ai_talk}\n')
        else:
            print('pls try again')

chat()
