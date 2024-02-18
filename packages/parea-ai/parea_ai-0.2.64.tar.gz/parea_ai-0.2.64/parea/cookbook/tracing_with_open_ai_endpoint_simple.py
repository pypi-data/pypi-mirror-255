import os

from dotenv import load_dotenv

load_dotenv("/Users/joschkabraun/dev/project_zero_prompt_engineering/parea-sdk/.env")


from openai import OpenAI

from parea import Parea

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# All you need to do is add these two lines
p = Parea(api_key=os.getenv("PAREA_API_KEY"))  # replace with your API key
p.wrap_openai_client(client)

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    temperature=0.5,
    messages=[
        {
            "role": "user",
            "content": "Write a Hello World program in Golang using FastAPI.",
        }
    ],
)
print(response.choices[0].message.content)
