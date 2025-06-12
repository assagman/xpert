import sys
import json
import asyncio
from typing import AsyncGenerator, Any, Optional, cast
import click
from pathlib import Path
from dotenv import load_dotenv

from pydantic import BaseModel, ConfigDict
from pydantic_core import core_schema
from pydantic_ai.agent import Agent
from pydantic_ai.result import StreamedRunResult
from pydantic_ai.exceptions import ModelHTTPError

from xpert.config import DefaultConfig


load_dotenv(Path("~/.xpert/.env").expanduser())


class CustomStreamedRunResult(StreamedRunResult):
    def __init__(self, obj: Any):
        self.obj = obj  # Store the original StreamedRunResult object

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: Any) -> core_schema.CoreSchema:
        # Treat as a generic object to bypass validation
        return core_schema.any_schema()


class AgentRunStreamResponse(BaseModel):
    message: Optional[str] = None
    is_completed: bool
    full_response: Optional[CustomStreamedRunResult] = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True
    )


def get_user_multiline_input():
    """
    Prompts the user for multiline input, allowing large pasted texts.
    Input ends when the user types '!' on a new line by itself.
    Typing 'q!' on a new line by itself exits the program.
    Returns:
        str: The collected multiline input from the user.
    """
    click.echo("[USER]:")
    click.echo()
    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            click.echo("\nEOF detected. Ending input.")
            break
        if line.strip() == "!":
            break
        if line.strip() == "q!":
            click.echo("Exiting program.")
            sys.exit(0)
        lines.append(line)
    user_multiline_input = "\n".join(lines)
    return user_multiline_input


async def agent_run_stream(agent: Agent, prompt, message_history=None) -> AsyncGenerator[AgentRunStreamResponse, Any]:
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
                    #         if char not in [" ", "\n"]: # Small delay for streaming effect
                    #             await asyncio.sleep(0.015) # Reduced delay for faster output
                    yield AgentRunStreamResponse(
                        message=None,
                        is_completed=True,
                        full_response=cast(CustomStreamedRunResult, response),
                    )
                    # click.echo()
                    # click.echo()
                    # click.echo("---")
                    # click.echo(f"Tokens Used: {response.usage().total_tokens}") # More specific usage
                    # click.echo("---")
                    # click.echo()
                    # await asyncio.sleep(0.5) # Reduced sleep
        except ModelHTTPError as err:
            if err.status_code == 403:
                print(f"""
                    Error type: {type(err)}
                    Error message: {err.message}
                """)
                raise err
        except Exception as exp:
            print(f"Unknown error: {exp}")
            print(exp)


async def _cli_stream_chat(agent: Agent):
    click.echo("Enter your text. Type '!' on a new line by itself to finish, or 'q!' to quit.")
    message_history = None
    while True:
        user_input = get_user_multiline_input()
        click.echo()
        click.echo("[AI]:")
        async for ars_response in agent_run_stream(agent, user_input, message_history=message_history):
            if not ars_response.is_completed:
                msg = ars_response.message
                if msg:
                    for ch in msg:
                        print(ch, end="")
                        sys.stdout.flush()
                        if ch not in [" ", "\n"]:
                            await asyncio.sleep(0.007)  # Small delay for smooth typing effect
            else:
                full_response = ars_response.full_response
                if full_response:
                    message_history = full_response.all_messages()
                    print()
                    print("📊")
                    print("Usage:")
                    usage = full_response.usage()
                    usage_display_dict = {
                        "requests": usage.requests,
                        "request_tokens": usage.request_tokens,
                        "response_tokens": usage.response_tokens,
                        "total_tokens": usage.total_tokens,
                        "details": usage.details,
                    }
                    print(json.dumps(usage_display_dict, indent=2))
                    print("📊")
                    print()
                else:
                    raise ValueError("Agent run stream returned None reponse")

@click.group()
def xp():
    """A command-line tool for interacting with AI agents."""
    pass


@xp.command()
@click.option("--provider", default=DefaultConfig.provider,
              help="Specify the AI model provider name to use.")
@click.option("--model", default=DefaultConfig.model_name,
              help="Specify the AI model name to use.")
@click.option("--temperature", type=float, default=DefaultConfig.model_settings.get("temperature"),
              help="Set the temperature for the AI model.")
def chat(provider: str, model: str, temperature: float):
    """
    Opens a basic chat session with an AI agent.
    """
    click.echo("🏗️ Under construction 🏗️")
    click.echo()
    click.echo(f"Using model: {model}")
    click.echo(f"Model settings:")
    click.echo(f"  * temperature: {temperature}")
    click.echo()
    agent = Agent(
        name="simple_agent_1",
        model=f"{provider}:{model}",
        system_prompt="",
        output_type=str,
        mcp_servers=[],
        tools=[],
        model_settings={
            "temperature": temperature,
        },
        retries=2,
    )

    asyncio.run(_cli_stream_chat(agent=agent))


# pyproject.toml entry point
def main_sync():
    """
    Synchronous entry point for the 'xp' command.
    Calls the Click command group.
    """
    xp()


if __name__ == "__main__":
    main_sync()
