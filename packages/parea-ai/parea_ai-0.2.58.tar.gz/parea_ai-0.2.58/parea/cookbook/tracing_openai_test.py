import os

import openai

from parea import Parea

# client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))  # replace with your API key
p = Parea(api_key=os.getenv("PAREA_API_KEY"))  # replace with your API key
p.wrap_openai_client(openai)

response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    temperature=0.5,
    messages=[
        {
            "role": "user",
            "content": "Write a Hello World program in Python using FastAPI.",
        }
    ],
)
print(response.choices[0].message["content"])
