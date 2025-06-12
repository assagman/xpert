from pydantic_ai.agent import Agent


class SimpleAgent:

    def __new__(cls, *args, **kwargs):
        return Agent(*args, **kwargs)
