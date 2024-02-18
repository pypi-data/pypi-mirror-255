import os

from parea import Parea, trace, trace_insert
from parea.schemas import Completion, LLMInputs, Log, Message, ModelParams, Role

p = Parea(api_key="pai-83bc9a58b025773fae7bc1e8b2518d32c4c5862f70116a1124021af0e46d046f")


def eval_func(log: Log) -> float:
    print()
    print(log.target)
    print(log.inputs)
    from random import random
    from time import sleep

    sleep(random() * 10)
    return random()


# annotate the function with the trace decorator and pass the evaluation function(s)
@trace(eval_funcs=[eval_func])
async def func(problem: str):
    return p.completion(
        data=Completion(
            llm_configuration=LLMInputs(
                model="gpt-3.5-turbo",
                model_params=ModelParams(temp=1),
                messages=[
                    Message(role=Role.user, content=f"Solve this math problem {problem}"),
                ],
            )
        )
    ).content


if __name__ == "__main__":
    p.experiment(
        data="Math problems",  # this is the name of my Test Collection in Parea (TestHub page)
        func=func,
    ).run()
