import asyncio
import json
import os

from dotenv import load_dotenv
from openai import AsyncOpenAI, OpenAI

from parea import Parea, trace

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
# client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

parea = Parea(api_key=os.getenv("PAREA_API_KEY"), project_name="testing")
parea.wrap_openai_client(client)


@trace
async def acall_llm(data: list[dict], model: str = "gpt-3.5-turbo", temperature: float = 0.0) -> str:
    stream = await client.chat.completions.create(model=model, temperature=temperature, messages=data, stream=True)
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")


def call_llm(data: list[dict], model: str = "gpt-3.5-turbo", temperature: float = 0.0) -> str:
    stream = client.chat.completions.create(model=model, temperature=temperature, messages=data, stream=True)
    for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")


# import asyncio
#
asyncio.run(acall_llm([{"role": "user", "content": "Is this async streaming?"}], model="gpt-3.5-turbo-1106"))

# call_llm(
#         [
#         {
#             "role": "user",
#             "content": "Is this sync streaming?"
#         }
#         ],
#         model="gpt-3.5-turbo-1106")


@trace("async function_calling")
async def function_calling():
    user_input = "I'm hungry"

    functions = [
        {
            "name": "call_google_places_api",
            "description": f"""
                This function calls the Google Places API to find the top places of a specified type near
                a specific location. It can be used when a user expresses a need (e.g., feeling hungry or tired) or wants to
                find a certain type of place (e.g., restaurant or hotel).
            """,
            "parameters": {"type": "object", "properties": {"place_type": {"type": "string", "description": "The type of place to search for."}}},
            "result": {"type": "array", "items": {"type": "string"}},
        }
    ]

    customer_profile_str = json.dumps(
        {
            "name": "John Doe",
            "location": {
                "latitude": 37.7955,
                "longitude": -122.4026,
            },
            "preferences": {
                "food": ["Italian", "Sushi"],
                "activities": ["Hiking", "Reading"],
            },
            "behavioral_metrics": {
                "app_usage": {"daily": 2, "weekly": 14},  # hours  # hours
                "favourite_post_categories": ["Nature", "Food", "Books"],
                "active_time": "Evening",
            },
            "recent_searches": ["Italian restaurants nearby", "Book clubs"],
            "recent_interactions": ["Liked a post about 'Best Pizzas in New York'", "Commented on a post about 'Central Park Trails'"],
            "user_rank": "Gold",  # based on some internal ranking system
        }
    )

    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "system",
                "content": f"You are a sophisticated AI assistant, "
                f"a specialist in user intent detection and interpretation. "
                f"Your task is to perceive and respond to the user's needs, even when they're expressed "
                f"in an indirect or direct manner. You excel in recognizing subtle cues: for example, "
                f"if a user states they are 'hungry', you should assume they are seeking nearby dining "
                f"options such as a restaurant or a cafe. If they indicate feeling 'tired', 'weary', "
                f"or mention a long journey, interpret this as a request for accommodation options like "
                f"hotels or guest houses. However, remember to navigate the fine line of interpretation "
                f"and assumption: if a user's intent is unclear or can be interpreted in multiple ways, "
                f"do not hesitate to politely ask for additional clarification. Make sure to tailor your "
                f"responses to the user based on their preferences and past experiences which can "
                f"be found here {customer_profile_str}",
            },
            {"role": "user", "content": user_input},
        ],
        temperature=0,
        functions=functions,
        stream=True,
    )
    async for chunk in stream:
        print(chunk.choices[0].delta.content or "", end="")

    # await asyncio.sleep(15)
    # if response.choices[0].message.function_call:
    #     function_call = response.choices[0].message.function_call
    #     msg = f'function_call: {function_call}'
    # else:
    #     msg = 'no function_call'
    # print(msg)
    # return msg


if __name__ == "__main__":
    # function_calling()

    asyncio.run(function_calling())
