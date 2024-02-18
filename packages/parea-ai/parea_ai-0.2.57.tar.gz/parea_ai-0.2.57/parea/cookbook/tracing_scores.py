import os

from parea import Parea, trace
from parea.schemas.log import Log

p = Parea(api_key=os.getenv("PAREA_API_KEY"))


def relevancy(log: Log) -> float:
    return 0.8


def matches_target(log: Log) -> float:
    return 0.6


def supported_by_context(log: Log) -> float:
    return 0.9


@trace(eval_funcs=[relevancy, matches_target, supported_by_context])
def f(query: str) -> str:
    return "hello"


if __name__ == "__main__":
    f("hello")
