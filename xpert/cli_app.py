import asyncio
import click

from xpert.config import DefaultConfig, load_env_vars
from xpert.chat.simple import cli_stream_chat


load_env_vars()


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

    agent_model = f"{provider}:{model}"
    agent_model_settings = {
        "temperature": temperature
    }

    asyncio.run(cli_stream_chat(agent_model, agent_model_settings))


# pyproject.toml entry point
def main_sync():
    """
    Synchronous entry point for the 'xp' command.
    Calls the Click command group.
    """
    xp()


if __name__ == "__main__":
    main_sync()
