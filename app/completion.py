#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
import os
import backoff
import openai 
import time
from openai import OpenAI

import json

client = OpenAI(api_key=os.getenv("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"))

assistant = client.beta.assistants.retrieve("asst_0p9BODU7E2a1xd9rdqtwm7c4")

#api_version="2023-03-15-preview"
import tiktoken

#if os.getenv("OPENAI_API_BASE"):
    # TODO: The 'openai.api_base' option isn't read in the client API. You will need to pass it when you instantiate the client, e.g. 'OpenAI(api_base=os.getenv("OPENAI_API_BASE"))'
    # openai.api_base = os.getenv("OPENAI_API_BASE")
#    if "azure" in os.getenv("OPENAI_API_BASE"):

system_prompt = '''As a technical writer editor on the documentation team for an MLOps platform, provide an in-depth review of the
following pull request git diff data. Your task is to carefully analyze the title, body, and
changes made in the pull request and identify any grammar and spelling issues that need addressing. 
Additionally, highlight ways the text could be made more clear and direct with suggestions for overall flow and writing best practices.
Please provide clear descriptions of each problem and offer constructive 
suggestions for how to address them. You should focus on providing feedback that will help
improve the quality of the documentaton set while also remaining concise and clear in your
explanations. Please note that unnecessary explanations or summaries should be avoided
as they may delay the review process. Your feedback should be provided in a timely
manner, using language that is easy to understand and follow.
'''

def show_json(obj):
    print(json.loads(obj.model_dump_json()))

def wait_on_run(run, thread):
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    return run

class OpenAIClient:
    '''OpenAI API client'''

    def __init__(self, model, temperature, frequency_penalty, presence_penalty,
                 max_tokens=4000, min_tokens=256):
        self.model = model
        self.temperature = temperature
        self.frequency_penalty = frequency_penalty
        self.presence_penalty = presence_penalty
        self.encoder = tiktoken.get_encoding("gpt2")
        self.max_tokens = max_tokens
        self.min_tokens = min_tokens
        self.openai_kwargs = {'model': self.model}
        if openai.api_type == "azure":
            self.openai_kwargs = {'engine': self.model}


    @backoff.on_exception(backoff.expo,
                          (openai.RateLimitError,
                           openai.APIConnectionError,
                           openai.InternalServerError),
                          max_time=300)
    def get_completion(self, prompt) -> str:
        if self.model.startswith("gpt-"):
            return self.get_completion_chat(prompt)
        else:
            return self.get_completion_text(prompt)
        

    def get_completion_chat(self, prompt) -> str:
        '''Invoke OpenAI API to get chat completion'''

        print('I"M before my janky code"')
        # my janky code
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        print('I"M IN my janky code"')
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        run = wait_on_run(run, thread)

        messages = client.beta.threads.messages.list(thread_id=thread.id)
        show_json(messages)
        
        completion_text = ''
        for m in messages:
            completion_text +=(f"{m.content[0].text.value}")
        
        print(completion_text)
        return completion_text

        completion_text = ''
        for event in response:
            if event["choices"] is not None and len(event["choices"]) > 0:
                choice = event["choices"][0]
                if choice.get("delta", None) is not None and choice["delta"].get("content", None) is not None:
                    completion_text += choice["delta"]["content"]
                if choice.get("message", None) is not None and choice["message"].get("content", None) is not None:
                    completion_text += choice["message"]["content"]
        return completion_text

        return show_json(messages)
    



        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]
        response = client.chat.completions.create(messages=messages,
        temperature=self.temperature,
        frequency_penalty=self.frequency_penalty,
        presence_penalty=self.presence_penalty,
        request_timeout=100,
        max_tokens=self.max_tokens - len(self.encoder.encode(f'{system_prompt}\n{prompt}')),
        stream=True, **self.openai_kwargs)

        completion_text = ''
        for event in response:
            if event["choices"] is not None and len(event["choices"]) > 0:
                choice = event["choices"][0]
                if choice.get("delta", None) is not None and choice["delta"].get("content", None) is not None:
                    completion_text += choice["delta"]["content"]
                if choice.get("message", None) is not None and choice["message"].get("content", None) is not None:
                    completion_text += choice["message"]["content"]
        return completion_text

    def get_completion_text(self, prompt) -> str:
        '''Invoke OpenAI API to get text completion'''

        print('I"M before my janky code"')
        # my janky code
        thread = client.beta.threads.create()
        message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt
        )
        print('I"M IN my janky code"')
        run = client.beta.threads.runs.create(
            thread_id=thread.id,
            assistant_id=assistant.id
        )

        run = wait_on_run(run, thread)
        show_json(run)

        messages = client.beta.threads.messages.list(
            thread_id=thread.id
        )

        print('I"M after my janky code"')




        prompt_message = f'{system_prompt}\n{prompt}'
        response = client.completions.create(prompt=prompt_message,
        temperature=self.temperature,
        best_of=1,
        frequency_penalty=self.frequency_penalty,
        presence_penalty=self.presence_penalty,
        request_timeout=100,
        max_tokens=self.max_tokens - len(self.encoder.encode(prompt_message)),
        stream=True, **self.openai_kwargs)

        completion_text = ''
        for event in response:
            if event["choices"] is not None and len(event["choices"]) > 0:
                completion_text += event["choices"][0]["text"]
        return completion_text
    
    

    def get_pr_prompt(self, title, body, changes) -> str:
        '''Generate a prompt for a PR review'''
        prompt = f'''Here are the title, body and changes for this pull request:
        

Title: {title}

Body: {body}

Changes:
```
{changes}
```
    '''
        return prompt

    def get_file_prompt(self, title, body, filename, changes) -> str:
        '''Generate a prompt for a file review'''
        prompt = f'''Here are the title, body and changes for this pull request:

Title: {title}

Body: {body}

And bellowing are changes for file {filename}:
```
{changes}
```
    '''
        return prompt
