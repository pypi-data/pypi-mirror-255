#!/usr/bin/env python3

import re
import sys
import subprocess

from dotenv import load_dotenv
from octoai.client import Client

load_dotenv()

client = Client()


def execute():
    completion = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are bash scripting, your output will be used directly on the command line, therefore "
                           "only provide the command and do not explain the command."
            },
            {
                "role": "user",
                "content": "The task: " + ' '.join(sys.argv[1:])
            }
        ],
        model="mixtral-8x7b-instruct-fp16",
        max_tokens=128,
        presence_penalty=0,
        temperature=0.5,
        top_p=0.2,
    )

    res = completion.__dict__['choices'][0].__dict__['message'].__dict__['content']

    pattern = r'```([^`]+)```'

    # Find all matches
    matches = re.findall(pattern, res, re.MULTILINE | re.DOTALL)

    # Extract the content between the "```"
    if matches:
        command = matches[0]
    else:
        command = res

    # Define the command you want to execute

    # Execute the command
    result = subprocess.run(command, shell=True, capture_output=True, text=True)

    # Check the result
    if result.returncode == 0:
        print(result.stdout)
    else:
        print("Error executing command. Error message: ")
        print(result.stderr)


