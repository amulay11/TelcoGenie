from flask import Flask, redirect, url_for, render_template, request
import os, json, ast
import openai
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt
from functions import init_conversation, get_chat_completions, get_billing_info, get_balance_info, get_customer_details, get_plan_recommendations, moderation_check

# Read the OpenAI API key
openai.api_key = open("C:/Users/Abhishek Mulay/Desktop/UpgradAIML/GENAI/chavi.txt", "r").read().strip()
os.environ['OPENAI_API_KEY'] = openai.api_key


app = Flask(__name__)

conversation_bot = []
conversation = init_conversation()
introduction = get_chat_completions(conversation)[0]
conversation_bot.append({'bot':introduction})


@app.route("/")
def default_func():
    global conversation_bot,conversation
    return render_template("index_invite.html", name_inp = conversation_bot)

@app.route("/end_conv", methods = ['POST','GET'])
def end_conv():
    global conversation_bot, conversation
    conversation_bot = []
    conversation = ''
    conversation = init_conversation()
    introduction = get_chat_completions(conversation)[0]
    conversation_bot.append({'bot':introduction})
    return redirect(url_for('default_func'))

@app.route("/invite", methods = ['POST'])
def invite():
    global conversation_bot, conversation
    output = ''
    user_input = request.form["user_input_message"]
    moderation = moderation_check(user_input)
    if moderation == 'Flagged':
        print("Sorry, this message has been flagged. Please restart your conversation.")
        return redirect(url_for('end_conv'))
        
    conversation.append({"role": "user", "content": user_input})
    conversation_bot.append({'user':user_input})
        
    response_assistant = get_chat_completions(conversation)
                
    moderation = moderation_check(response_assistant[0])
    if moderation == 'Flagged':
        print("Sorry, this message has been flagged. Please restart your conversation.")
        return redirect(url_for('end_conv'))
    if response_assistant[1]:
        #print("Inside function calling")
        conversation.append(({"role": "function", "name":response_assistant[1], "content": response_assistant[0]}))
        print("\n" + str(response_assistant[0]) + "\n")
        response_assistant = get_chat_completions(conversation)
        conversation.append({"role": "assistant", "content": str(response_assistant[0])})
        conversation_bot.append({'bot':str(response_assistant[0])})
        print("\n" + str(response_assistant[0]) + "\n")
    else:
        conversation.append(({"role": "assistant", "content": response_assistant[0]}))
        conversation_bot.append({'bot':str(response_assistant[0])})
        print("\n" + str(response_assistant[0]) + "\n")
    return redirect(url_for('default_func'))

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")