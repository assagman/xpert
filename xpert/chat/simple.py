import sys
from typing import Any, Optional, AsyncGenerator, cast, Dict
import json
import asyncio

from pydantic import BaseModel, ConfigDict
from pydantic_core import core_schema
from pydantic_ai.agent import Agent
from pydantic_ai.result import StreamedRunResult
from pydantic_ai.exceptions import ModelHTTPError


class CustomStreamedRunResult(StreamedRunResult):
    def __init__(self, obj: Any):
        self.obj = obj  # Store the original StreamedRunResult object

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: Any
    ) -> core_schema.CoreSchema:
        # Treat as a generic object to bypass validation
        return core_schema.any_schema()


class AgentRunStreamResponse(BaseModel):
    message: Optional[str] = None
    is_completed: bool
    full_response: Optional[CustomStreamedRunResult] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


def get_user_multiline_input():
    """
    Prompts the user for multiline input, allowing large pasted texts.
    Input ends when the user types '!' on a new line by itself.
    Typing 'q!' on a new line by itself exits the program.
    Returns:
        str: The collected multiline input from the user.
    """
    print("[USER]:")
    print()
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            print("\nEOF detected. Ending input.")
            break
        if line.strip() == "!":
            break
        if line.strip() == "q!":
            print("Exiting program.")
            sys.exit(0)
        lines.append(line)
    user_multiline_input = "\n".join(lines)
    return user_multiline_input


async def agent_run_stream(
    agent: Agent, prompt, message_history=None
) -> AsyncGenerator[AgentRunStreamResponse, Any]:
    try:
        async with agent.run_stream(
            prompt,
            message_history=message_history,
        ) as response:
            async for message in response.stream_text(delta=True):
                yield AgentRunStreamResponse(
                    message=message,
                    is_completed=False,
                    full_response=None,
                )
            yield AgentRunStreamResponse(
                message=None,
                is_completed=True,
                full_response=cast(CustomStreamedRunResult, response),
            )
    except ModelHTTPError as err:
        if err.status_code == 403:
            print(
                f"""
                    Error type: {type(err)}
                    Error message: {err.message}
                """
            )
            raise err
    except Exception as exp:
        print(f"Unknown error: {exp}")
        print(exp)


async def cli_stream_chat(agent_model: str, agent_model_settings: Dict):
    print(
        "Enter your text. Type '!' on a new line by itself to finish, or 'q!' to quit."
    )

    agent = Agent(
        name="simple_agent_1",
        model=agent_model,
        system_prompt="",
        output_type=str,
        mcp_servers=[],
        tools=[],
        model_settings=agent_model_settings,
        retries=2,
    )

    message_history = None
    while True:
        user_input = get_user_multiline_input()
        print()
        print("[AI]:")
        async for ars_response in agent_run_stream(
            agent, user_input, message_history=message_history
        ):
            if not ars_response.is_completed:
                msg = ars_response.message
                if msg:
                    for ch in msg:
                        print(ch, end="")
                        sys.stdout.flush()
                        if ch not in [" ", "\n"]:
                            await asyncio.sleep(
                                0.007
                            )  # Small delay for smooth typing effect
            else:
                full_response = ars_response.full_response
                if full_response:
                    message_history = full_response.all_messages()
                    print()
                    print("=" * 20)
                    print("📊 Usage:")
                    usage = full_response.usage()
                    usage_display_dict = {
                        "requests": usage.requests,
                        "request_tokens": usage.request_tokens,
                        "response_tokens": usage.response_tokens,
                        "total_tokens": usage.total_tokens,
                        "details": usage.details,
                    }
                    print(json.dumps(usage_display_dict, indent=2))
                    print("=" * 20)
                    print()
                else:
                    raise ValueError("Agent run stream returned None reponse")
