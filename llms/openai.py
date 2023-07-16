import openai
import json
import importlib
from typing import List
import time

class openaif():
    # To initialize, you'll need to pass your API key and list of functions.  You can change your model if you are using gpt4
    def __init__(self, api_key: str, messages: List=[]):
        self.api_key = api_key
        self.openai = openai
        self.model = 'gpt-4-0613' 
        self.openai.api_key = self.api_key
        self.openai.Engine.list()['data'][0]  # will throw an error if invalid key
        self.temperature = 0  #note: people have noticed chatGPT not including required parameters.  Setting temperature to 0 seems to fix that
        self.maximum_function_content_char_size = 2000 #to prevent token overflow
        self.messages = messages
        self.infinite_loop_counter = 0  #don't want to burn through too many openai credits :-)
        self.functions = [
            {
            "name": "create_issue",
            "description": "Creates a Jira Task or Bug.",
            "parameters": {
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "The Project Key",
                    },
                    "issue_type": {"type": "string", "enum": ["Task", "Bug"]},
                    "summary": {
                        "type": "string",
                        "description": "The summary title of the Task or Bug",
                    },
                    "description": {
                        "type": "string",
                        "description": "The detailed description of the Task or Bug",
                    },
                },
                "required": ["projectKey", "issuetype", "summary", "description"],
            },
        }
    ]


    def clear_chat_session(self):
        self.messages = []

    def user_request(self, prompt:str)-> str:
        self.messages.append({"role": "user", "content": prompt})
        res = self.call_openai()
        if res is str:
            return res
        if res['choices'][0]['message']:
            self.messages.append(res['choices'][0]['message'])
            while res['choices'][0]['finish_reason'] == 'function_call':
                    self.infinite_loop_counter += 1
                    if self.infinite_loop_counter > 100: exit() # you can do whatever you want, but if chatgpt is instructing continuous function calls, something needs to be looked at
                    function_name = res['choices'][0]['message']['function_call']['name']
                    # As mentioned, security is always a concern when allowing a 3rd party system to execute functions on your servers!!!
                    # This call assures that you've at least passed these functions to chatGPT.  
                    # You should also consider scrubbing the parameters to prevent SQL or other injections!

                    function_args = json.loads(res['choices'][0]['message']['function_call']['arguments'])
                    #module = importlib.import_module('.', package='atlassian.jira')
                    cls = getattr(importlib.import_module('atlassian.jira'), 'Jira')
                    obj = cls()
                    funct = getattr(obj, function_name)
                    function_response = str(funct(**function_args))  #responses must be string in order to append to messages
                    if len(function_response) > self.maximum_function_content_char_size: function_response = function_response[:self.maximum_function_content_char_size]
                    res = self.function_call(function_name, function_response)
                  
        return res['choices'][0]['message']['content']

    def function_call(self, function:str, function_response:str):
         self.messages.append({"role": "function", "name": function, "content": function_response})
         res = self.call_openai()
         if res['choices'][0]['message']:
             self.messages.append(res['choices'][0]['message'])
         return res

    def call_openai(self)->str:
        # We seem to get a lot of "System Overloaded" from chatGPT.  This will try 3 times otherwise return message.
        res = "I'm sorry.  OpenAI is currently overloaded.  Please try back later."
        attempt = 1
        while attempt < 3:
            try:
                if self.functions == []:
                    res = self.openai.ChatCompletion.create(
                    model=self.model,
                    temperature=self.temperature, 
                    messages=self.messages,
                    )
                else:
                    res = self.openai.ChatCompletion.create(
                    model=self.model,
                    temperature=self.temperature, 
                    messages=self.messages,
                    functions=self.functions
                    )

            except Exception as e:
                #wait one second and try again
                print(e)
                attempt += 1
                time.sleep(1)
                continue
            break

        return res

