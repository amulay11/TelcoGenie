import os, json, ast
import openai
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from functions import init_conversation, get_chat_completions, get_billing_info, get_balance_info, get_customer_details, get_plan_recommendations, moderation_check

# Read the OpenAI API key
openai.api_key = open("C:/Users/Abhishek Mulay/Desktop/UpgradAIML/GENAI/chavi.txt", "r").read().strip()
os.environ['OPENAI_API_KEY'] = openai.api_key

def dialogue_mgmt_system():
    conversation = init_conversation()

    introduction = get_chat_completions(conversation)[0]

    print(introduction + '\n')

    user_input = ''

    while(user_input.lower() != "exit"):

        user_input = input("")

        moderation = moderation_check(user_input)
        if moderation == 'Flagged':
            print("Sorry, this message has been flagged. Please restart your conversation.")
            break
        
        conversation.append({"role": "user", "content": user_input})
        
        response_assistant = get_chat_completions(conversation)
                
        moderation = moderation_check(response_assistant[0])
        if moderation == 'Flagged':
            print("Sorry, this message has been flagged. Please restart your conversation.")
            break
        if response_assistant[1]:
            #print("Inside function calling")
            conversation.append(({"role": "function", "name":response_assistant[1], "content": response_assistant[0]}))
            print("\n" + str(response_assistant[0]) + "\n")
            response_assistant = get_chat_completions(conversation)
            conversation.append({"role": "assistant", "content": str(response_assistant)[0]})
            print("\n" + str(response_assistant[0]) + "\n")
        else:
            conversation.append(({"role": "assistant", "content": response_assistant[0]}))
            print("\n" + str(response_assistant[0]) + "\n")

dialogue_mgmt_system()