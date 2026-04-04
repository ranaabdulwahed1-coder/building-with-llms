from tools import call_LLM, mod_input, mod_output
def main():
    while True: #main loop
        while True:# secondary loop to insure constant prompting
            category = input("Pick a category (Science, History, Sports, Art): ")
            if category.lower() == 'quit':
                break
            elif mod_input(category) != 'safe':
                print('please try again')
            elif category.lower() not in ['science', 'history', 'sports', 'art']:
                print('please enter a valid category')
            else:
                break
        if category.lower() == 'quit':
            break

        question, ideal = get_question(category)
        print(question)

        while True:
            user_answer = input('you: ')
            result = get_explan(question, user_answer, ideal)
            if eval_1(question, result, ideal) == 'true':
                break
            else:
                print("Incorrect, try again")

        if eval_2(question, result, ideal) not in ['2', '3']:
            result = get_explan(question, user_answer, ideal)

        if mod_output(result) != 'safe':
            print("Something went wrong, try again")
        else:
            print(result)






def get_question(category):
    convo = [
        {"role": "system", "content": """You are a trivia bot. generate one trivia question
        and its correct answer.
         you MUST respond in exactly this format with no other text:
         Question: [question here] | Answer: [answer here]"""},
        {"role": "user", "content": f"Category: {category}"}

]
    response = call_LLM(convo)
    question, ideal = response.split("|")
    return question, ideal
def get_explan(question, user_answer, ideal):
    user_message = f"Question: {question} | User Answer: {user_answer} | Correct Answer: {ideal}"
    convo = [{'role' : 'system', 'content' : """ you are a friendly trivia host.
you will be given a question, the player's answer, and the correct answer.
If the player was right, congratulate them and explain why the answer is correct in an interesting way.
If the player was wrong, encouragingly tell them the correct answer and explain why in a fun way.
Keep it short no more than 50 words, talk directly to the player using 'you'"""}, {'role': 'user', 'content': user_message}]
    response = call_LLM(convo)
    return response
def eval_1(question, agent , ideal):
    user_message = f"Question: {question} | Agent Response : {agent} | Correct Answer: {ideal}"
    convo = [{'role' : 'system', 'content' : """ you are a critic make sure that the facts of the response
              match with what is said in the ideal if there are any discrepencies only output 'false'
              else respond with only 'true' """},
              {'role': 'user', 'content': user_message}]
    response = call_LLM(convo)
    return response
def eval_2(question, explanation, ideal):
    user_message = f"Question: {question} | Agent Response : {explanation} | Correct Answer: {ideal}"
    convo = [{'role' : 'system', 'content' : """ your job is to critic the reponse,you have to grade the response
              give one point for good explantion style, one point for clear language, one point if useful information
              recieved. at the end of your grading only return the number of points the response recieve
              '1' '2' or '3' """},
              {'role': 'user', 'content': user_message}]
    response = call_LLM(convo)
    return response
main()
