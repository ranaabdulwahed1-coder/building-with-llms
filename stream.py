from openai import OpenAI        # loads libary
from dotenv import load_dotenv   # allows to read the file
import os                        # python tool for accessing system stuff

load_dotenv()                    # reads the .env file right now

client = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),   # grabs the key
    base_url="https://openrouter.ai/api/v1"    
)
def chat():
    convo = []
    print(' What is on your mind(type quit or goodbye to end chat)\n')
    while True:
        user_input = input('you: ')
        if user_input.lower() in ['quit', 'goodbye']:
            print(' adios brochacho')
            break
        convo.append({'role' : 'user', 'content' : user_input})
        response = client.chat.completions.create(
            model = 'stepfun/step-3.5-flash:free',
            max_tokens = 1000,
            messages = convo,
            stream = True,
        )
        print('\nClaude: ', end='', flush=True)
        full_reply = ''
        for chunk in response:
            piece = chunk.choices[0].delta.content or ''
            print(piece, end= '', flush = True)
            full_reply += piece
        print('\n')


        convo.append({'role' : 'assistant', 'content' : full_reply})

chat()





