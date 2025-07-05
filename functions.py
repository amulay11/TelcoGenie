import os, json, ast
import openai
from openai import OpenAI
from tenacity import retry, wait_random_exponential, stop_after_attempt


def init_conversation():
    '''
    Returns a list [{"role": "system", "content": system_message}]
    '''

    delimiter = "####"

    
    
    system_message = f"""
    You are an intelligent telecom customer service specialist and your goal is to help users with their queries.
    You need to ask relevant questions and understand the users intent by analysing the user's responses.
    You specialize in dealing with mobile customers. 
    The type of user queries that you can help with are:
    1. Prepaid mobile balance enquiry
    2. Postpaid mobile billing enquiry
    3. Get current Plan details
    4. Recommend top plans based on user's requirement
    
    First you must identify the user's intent. 
    Then you should make use of the supplied tools to assist the user and answer their queries.
    
    {delimiter}
    While using the supplied tools, ensure that you are passing the correct parameter values as per the specifications.
    {delimiter}
    
    Follow the chain-of-thoughts below: \n
    {delimiter}
    Thought 1: Ask a question to understand the user's intent. \n
    If their intent is unclear. Ask followup questions to understand their intent.
    
    You need to first be clear about the user's intent. 
    If the intent is one of the following then you proceed to next thought:
    1. Prepaid mobile balance enquiry
    2. Postpaid mobile billing enquiry
    3. Get current Plan details
    4. New mobile connection or change plan
    
    If the intent is different from any of the above then you tell the user that you will redirect their query to a 
    human assistant and mention that they will soon be connected to a human assistant to help them with their query.
    
    In case you do not have an appropriate tool to be called then continue with the conversation.

    {delimiter}
    Thought 2: Lets say the users intent is one of the below:
    1. Prepaid mobile balance enquiry
    2. Postpaid mobile billing enquiry
    3. Get current plan details
    4. New mobile connection
    5. Change plan
    Check the tools supplied and call the appropriate tool based on the intent.
        
    {delimiter}
    
    {delimiter}
    Thought 3: 
    Do not assume or manipulate the values for any of the parameters input to the tool. 
    You are supposed to get complete understanding of users requirement on all aspects.
    You cannot assume user preferences on any of the aspects like International calls or OTT.
    If the user preference is not clear to you, then ask more questions, do not assume or manipulate the parameter values.
    You must ask question with a sound logic as opposed to directly citing the key you want to understand value for.
    You will be heavily penalised if you manipulate any parameter values without understanding the users requirement.
            
    {delimiter}

    {delimiter}
    Thought 4: Check if you have populated the input parameter values correctly if you are calling a tool.
    For calling the functions get_billing_info or get_balance_info, you must supply value of "Mobile Number" in the input. 
    You will be heavily penalised if you do not follow this instruction.
    If you are not confident about any of the values, ask clarifying questions.
    {delimiter}
    
    {delimiter}
    Thought 5: While asking for the Mobile Number, it is better to specify the expected length
    For example : Please provide your 10 digit mobile number.
    {delimiter}
    
    {delimiter}
    Thought 6: When the user asks for a new mobile connection or a plan change, ask user preferences using questions framed with sound logic.
    You should not ask multiple questions in one go.
    Below is a bad example of asking questions as here multiple questions are asked with direct refernce to low/medium/high values.
    'To help you with a new mobile connection, I need to understand your usage preferences. This will help me recommend the best plans for you. Could you please let me know:\n\n1. Your data usage preference (low, medium, high)?\n2. Your voice usage preference (low, medium, high)?\n3. Your SMS usage preference (low, medium, high)?\n4. Your use of international calling (low, medium, high)?\n5. Your use of international roaming (low, medium, high)?\n6. Your interest in OTT services (low, medium, high)?\n7. Your monthly budget for the mobile plan?'
    A better way to frame the question would be as below :
    'To help you with a new mobile connection, I need to understand your usage preferences. This will help me recommend the best plans for you. Could you please let me know if you use a lot of mobile data on a daily basis?'
    Once the user has answered you can move to the next logical question.
    {delimiter}
    
    {delimiter}
    Thought 7: The functions get_billing_info and get_balance_info will provide a response in a json format. 
    You need to use the details to answer the specific query from the user.
    If the answer to user's query is not available in the response provided by the tools then advise the user that you will connect him/her to a human assistant for further help.
    {delimiter}
    
    {delimiter}
    Thought 8: The function get_plan_recommendations will output a string containing a list of dictionaries.
    Each dictionary in the list represents the details of one plan.
    You need to use these details and recommend the plans to the users in the increasing order of monthly budget.
    You recommend each plan to the user as a sales expert highlighting its key features so that the user will be interested to enroll for the plan. 
    If the function does not return any plan in the response then advise the user that you will connect him/her to a human assistant for further help.
    User may ask more queries about the plans, answer them based on the recommended plans data you have. If the answer to user's query is not available then advise the user that you will connect him/her to a human assistant for further help.
    {delimiter}
    
    
    Start with a short welcome message and encourage the user to share their requirements.
    """
    conversation = [{"role": "system", "content": system_message}]
    # conversation = system_message
    return conversation

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_balance_info",
            "description": "Get the prepaid balance information for a mobile subscriber. Call this whenever you need to know prepaid balance related information, for example when a customer asks 'I have an issue with my prepaid number' or 'I want to know my mobile balance'",
            "parameters": {
                "type": "object",
                "properties": {
                    "Mobile_Number": {
                        "type": "string",
                        "description": "The customer's Mobile Number.",
                    }
                },
                "required": ["Mobile_Number"],
                "additionalProperties": False,
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_billing_info",
            "description": "Get the postpaid billing information for a mobile subscriber. Call this whenever you need to know postpaid billing related information, for example when a customer asks 'I have a billing issue' or 'I want to know my bill due date'",
            "parameters": {
                "type": "object",
                "properties": {
                    "Mobile_Number": {
                        "type": "string",
                        "description": "The customer's Mobile Number.",
                    }
                },
                "required": ["Mobile_Number"],
                "additionalProperties": False,
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_customer_details",
            "description": "Get the customer details for a mobile subscriber including the plan details. Call this whenever the user asks for subscription details or plan details or activation date",
            "parameters": {
                "type": "object",
                "properties": {
                    "Mobile_Number": {
                        "type": "string",
                        "description": "The customer's Mobile Number.",
                    }
                },
                "required": ["Mobile_Number"],
                "additionalProperties": False,
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_plan_recommendations",
            "description": "Get top plan recommendations for a mobile subscriber. The subscriber may be a new customer who wants a new connection or an existing subscriber who wants to change the plan. Call this whenever you need to provide plan recommendations to a user, for example when a user asks 'I want a new mobile connection' or 'I want to change my mobile plan'",
            "parameters": {
                "type": "object",
                "properties": {
                    "Data_Usage": {
                        "type": "string",
                        "enum": ["low","medium","high"],
                        "description": "The user's preference on Data Usage (low/medium/high).",
                    },
                    "Voice_Usage": {
                        "type": "string",
                        "enum": ["low","medium","high"],
                        "description": "The user's preference on Voice Usage (low/medium/high).",
                    },
                    "SMS_Usage": {
                        "type": "string",
                        "enum": ["low","medium","high"],
                        "description": "The user's preference on SMS Usage (low/medium/high).",
                    },
                    "International_Calling": {
                        "type": "string",
                        "enum": ["low","medium","high"],
                        "description": "The user's preference on use of International Calling feature (low/medium/high).",
                    },
                    "International_Roaming": {
                        "type": "string",
                        "enum": ["low","medium","high"],
                        "description": "The user's preference on use of International Roaming feature (low/medium/high).",
                    },
                    "OTT_Usage": {
                        "type": "string",
                        "enum": ["low","medium","high"],
                        "description": "The user's preference on OTT usage (low/medium/high).",
                    },
                    "Monthly_Budget": {
                        "type": "integer",
                        "description": "The user's monthly budget.",
                    }
                },
                "required": ["Data_Usage", "Voice_Usage", "SMS_Usage", "International_Calling", "International_Roaming", "OTT_Usage", "Monthly_Budget"],
                "additionalProperties": False,
            }
        }
    }
]

import pandas as pd
import json

def get_customer_details(mobile_number, subscription_type = ''):
    
    df = pd.read_csv("telecom_subscribers_data.csv")
        
    # Check if both inputs are missing
    if not mobile_number:
        return json.dumps({"error": "Input missing please provide Mobile Number"})
    
    # Filter the DataFrame based on provided input
    if subscription_type:
        result = df[(df['Mobile Number'] == int(mobile_number)) & (df['Subscription Type'] == subscription_type)]
    else:
        result = df[df['Mobile Number'] == int(mobile_number)]
    
    # Check if any record is found
    if result.empty:
        print("No record found")
        return json.dumps({"error": "No record found for the provided input"})
    
    # Get the first matched record
    record = result.iloc[0]
    
    #json_data = result.to_dict(orient="records")
    #print(json_data)
    
    
    # Create the dictionary based on Subscription Type
    if record['Subscription Type'] == 'Prepaid':
        data = {
            "Mobile Number": int(record['Mobile Number']),
            "Customer ID": int(record['Customer ID']),
            "First Name": record['First Name'],
            "Last Name": record['Last Name'],
            "Subscription Type": record['Subscription Type'],
            "Subscription Status": record['Subscription Status'],
            "Price Plan": record['Price Plan'],
            "Activation Date": record['Activation Date'],
            "Cancellation Date": record['Cancellation Date'],
            "Total Prepaid Balance": float(record['Total Prepaid Balance']),
            "Prepaid Balance Used": float(record['Prepaid Balance Used']),
            "Prepaid Balance Remaining": float(record['Prepaid Balance Remaining']),
            "Last Recharge Amount": float(record['Last Recharge Amount']),
            "Last Recharge Date": record['Last Recharge Date']
        }
    elif record['Subscription Type'] == 'Postpaid':
        data = {
            "Mobile Number": int(record['Mobile Number']),
            "Customer ID": int(record['Customer ID']),
            "First Name": record['First Name'],
            "Last Name": record['Last Name'],
            "Subscription Type": record['Subscription Type'],
            "Subscription Status": record['Subscription Status'],
            "Price Plan": record['Price Plan'],
            "Activation Date": record['Activation Date'],
            "Cancellation Date": record['Cancellation Date'],
            "Last Billed Amount": float(record['Last Billed Amount']),
            "Last Bill Payment Amount": float(record['Last Bill Payment Amount']),
            "Last Bill Payment Date": record['Last Bill Payment Date'],
            "Pending Amount Due": float(record['Pending Amount Due']),
            "Bill Due Date": record['Bill Due Date']
        }
    else:
        return json.dumps({"error": "Invalid Subscription Type"})
    
    # Convert to native Python types
    # data = {key: (value.item() if hasattr(value, 'item') else value) for key, value in data.items()}
    
    # Convert the dictionary to a JSON object and return
    return json.dumps(data)
    

def get_billing_info(Mobile_Number = ''):
    response = get_customer_details(Mobile_Number, "Postpaid")
    return response

def get_balance_info(Mobile_Number = ''):
    response = get_customer_details(Mobile_Number, "Prepaid")
    return response

def plan_map(plan_description):
    delimiter = "#####"
    
    plan_spec = {
        "Data_Usage":"(Free Data allowed in GB)",
        "Voice_Usage":"(Free Voice allowed in minutes)",
        "SMS_Usage":"(Free SMS allowed)",
        "International_Calling":"(Is international calling included as a value added service)",
        "International_Roaming":"(Is international roaming included as a value added service)",
        "OTT_Usage": "(OTT platforms included in the plan)"
    }

    values = {'low','medium','high'}

    prompt=f"""
    You are a mobile plans Specifications Classifier whose job is to extract the key features of mobile plans and classify them as per their requirements.
    To analyze each mobile plan, perform the following steps:
    Step 1: Extract the plan's primary features from the description {plan_description}
    Step 2: Store the extracted features in {plan_spec} \
    Step 3: Classify each of the items in {plan_spec} into {values} based on the following rules: \
    {delimiter}
    Data_Usage:
    - low: <<< If free data in the plan is less than 25 GB >>> , \n
    - medium: <<< If free data in the plan is >= 25 GB and less than 100 GB >>> , \n
    - high: <<< If the free data in the plan is more than 100 GB or unlimited >>> , \n

    Voice_Usage:
    - low: <<< If free voice minutes is less than 300 >>> , \n
    - medium: <<< If free voice minutes is >= 300 and less than 1000 >>> , \n
    - high: <<< If free voice minutes is >=1000 or unlimited >>> \n

    SMS_Usage:
    - low: <<< If free SMS is up to 100 >>> , \n
    - medium: <<< if free SMS is between 100 and 1000 >>> , \n
    - high: <<< if free SMS is greater than 1000 or unlimited >>> \n

    International_Calling:
    - low: <<< If the value added service does not have International Calling >>> , \n
    - high: <<< If the value added service has International Calling >>> \n

    International_Roaming:
    - low: <<< If the value added service does not have International Roaming >>> , \n
    - high: <<< If the value added service has International Roaming >>> \n
    
    OTT_Usage:
    - low: <<< If there is no OTT offered in the plan >>> , \n
    - medium: <<< if there is only one OTT service offered in the plan >>> , \n
    - high: <<< if there are more than one OTT service offered in the plan >>> \n
    {delimiter}

    
    {delimiter}
    ### Strictly don't keep any other text in the values of the JSON dictionary other than low or medium or high ###
    ### The output must only have a JSON dictionary and no other characters before or after it. You will be heavily penalized if you do not follow this ###
    
    """
    input = f"""Follow the above instructions step-by-step and output the dictionary in JSON format {plan_spec} for the following plan {plan_description}. Return only the json in output and no extra characters"""
    #see that we are using the Completion endpoint and not the Chatcompletion endpoint
    messages=[{"role": "system", "content":prompt },{"role": "user","content":input}]

    # JSON return type specified
    MODEL = 'gpt-4o'
    chat_completion_json = openai.chat.completions.create(
            model=MODEL,
            response_format = { "type": "json_object"},
            messages=messages)

    #print(chat_completion_json.choices[0].message.content)
    #response = chat_completion_json.choices[0].message.content
    response = json.loads(chat_completion_json.choices[0].message.content)
    return response

def update_plan_data():
    plan_data = pd.read_csv("plan_data.csv")
    ##Run this code once to extract plan info in the form of a dictionary
    plan_df= pd.read_csv('plan_data.csv')

    ## Create a new column "plan_feature" that contains the dictionary of the plan features
    plan_df['plan_feature'] = plan_df['Description'].apply(lambda x: plan_map(x))

    plan_df.to_csv("updated_plan_data.csv",index=False,header = True)

def get_plan_recommendations(Data_Usage, Voice_Usage, SMS_Usage, 
                             International_Calling, International_Roaming, 
                             OTT_Usage, Monthly_Budget):
    plan_df = pd.read_csv('updated_plan_data.csv')
    budget = int(Monthly_Budget)
    # # Creating a copy of the DataFrame and filtering plans based on the budget
    filtered_plans = plan_df.copy()
    filtered_plans = filtered_plans[filtered_plans['Minimum Recharge/Monthly Recurring Amount'] <= budget].copy()
    
    user_requirements = {"Data_Usage":Data_Usage, "Voice_Usage":Voice_Usage,
                        "SMS_Usage":SMS_Usage, "International_Calling":International_Calling,
                        "International_Roaming":International_Roaming, "OTT_Usage":OTT_Usage}
    
    mappings = {'low': 0, 'medium': 1, 'high': 2}
    
    # # # Creating a new column 'Score' in the filtered DataFrame and initializing it to 0
    filtered_plans['Score'] = 0
    
    # # # Iterating over each plan in the filtered DataFrame to calculate scores based on user requirements
    for index, row in filtered_plans.iterrows():
        plan_match_str = row['plan_feature']
        plan_values = plan_match_str
        plan_values = ast.literal_eval(plan_match_str)
        score = 0
        
        # Comparing user requirements with laptop features and updating scores
        for key, user_value in user_requirements.items():
            plan_value = plan_values.get(key, None)
            plan_mapping = mappings.get(plan_value, -1)
            user_mapping = mappings.get(user_value, -1)
            if plan_mapping >= user_mapping:
                score += 1  # Incrementing score if laptop value meets or exceeds user value

        filtered_plans.loc[index, 'Score'] = score  # Updating the 'Score' column in the DataFrame
    
    # Sorting plans by score in descending order and selecting the top 3 plans
    top_plans = filtered_plans.drop('plan_feature', axis=1)
    top_plans = top_plans.sort_values('Score', ascending=False).head(3)
    top_plans_json = top_plans.to_json(orient='records')  # Converting the top laptops DataFrame to JSON format

    data = json.loads(top_plans_json)
    recommended_plans = []
    for i in range(len(data)):
        if data[i]['Score'] > 2:
            recommended_plans.append(data[i])
    
    output = str(recommended_plans)
    
    return output    

# Define a Chat Completions API call
# Retry up to 6 times with exponential backoff, starting at 1 second and maxing out at 20 seconds delay
@retry(wait=wait_random_exponential(min=1, max=20), stop=stop_after_attempt(6))
def get_chat_completions(input_msg, json_format = False):
    MODEL = "gpt-4o"

    system_message_json_output = """<<. Return output in JSON format to the key output.>>"""
    function_called = ''

    # If the output is required to be in JSON format
    if json_format == True:
        # Append the input prompt to include JSON response as specified by OpenAI
        input_msg[0]['content'] += system_message_json_output

        # JSON return type specified
        chat_completion_json = openai.chat.completions.create(
            model=MODEL,
            messages=input_msg,
            tools=tools)

        response_message = chat_completion_json.choices[0].message
        if dict(response_message).get('tool_calls'):

            # Which function call was invoked
            function_called = response_message.tool_calls[0].function.name
            #print("Function called:",function_called)

            # Extracting the arguments
            function_args  = json.loads(response_message.tool_calls[0].function.arguments)

            # Function names
            available_functions = {
              "get_billing_info": get_billing_info,
              "get_balance_info": get_balance_info,
              "get_customer_details": get_customer_details,
              "get_plan_recommendations": get_plan_recommendations
            }

            function_to_call = available_functions[function_called]
            output = function_to_call(*list(function_args .values()))

        else:
            output = json.loads(chat_completion_json.choices[0].message.content)

    # No JSON return type specified
    else:
        chat_completion = openai.chat.completions.create(
            model=MODEL,
            messages=input_msg,
            tools=tools)

        response_message = chat_completion.choices[0].message
        if dict(response_message).get('tool_calls'):

            # Which function call was invoked
            function_called = response_message.tool_calls[0].function.name
            #print("Function called:",function_called)

            # Extracting the arguments
            function_args  = json.loads(response_message.tool_calls[0].function.arguments)

            # Function names
            available_functions = {
              "get_billing_info": get_billing_info,
              "get_balance_info": get_balance_info,
              "get_customer_details": get_customer_details,
              "get_plan_recommendations": get_plan_recommendations
            }

            function_to_call = available_functions[function_called]
            output = function_to_call(*list(function_args .values()))

        else:
            output = chat_completion.choices[0].message.content

    return output, function_called

# Define a function called moderation_check that takes user_input as a parameter.

def moderation_check(user_input):
    # Call the OpenAI API to perform moderation on the user's input.
    response = openai.moderations.create(input=user_input)

    # Extract the moderation result from the API response.
    moderation_output = response.results[0].flagged
    # Check if the input was flagged by the moderation system.
    if response.results[0].flagged == True:
        # If flagged, return "Flagged"
        return "Flagged"
    else:
        # If not flagged, return "Not Flagged"
        return "Not Flagged"