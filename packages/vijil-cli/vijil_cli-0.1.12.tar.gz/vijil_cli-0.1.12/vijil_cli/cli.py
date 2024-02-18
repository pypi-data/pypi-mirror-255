import click
import requests
from vijil_cli.vijilapi.config_handler import save_config, remove_config
from vijil_cli.evaluations.commands import *

# VIGIL_API_BASE_URL = "http://127.0.0.1:8000/api/v1"
# VIGIL_API_BASE_URL = "https://develop.vijil.ai/api/v1"
VIGIL_API_BASE_URL = "https://score.vijil.ai/api/v1"

@click.group()
def main():
    """Welcome to Vijil CLI tool."""

@main.command()
@click.option('--username', prompt='Enter your username')
@click.option('--token', prompt='Enter your token', hide_input=True)
def login(username, token):
    """Login to Vijil CLI."""
    click.echo(f"Login Successful.")
    save_config(username, token)
    verify_url = f"{VIGIL_API_BASE_URL}/tokens/verify"
    data = {"username": username, "token": token}

    try:
        response = requests.post(verify_url, json=data)
        response.raise_for_status()

        if response.json().get("verify"):
            click.echo("Token verification successful. Configuration complete.")
        else:
            click.echo("Token verification failed. Please check your credentials.")

    except requests.exceptions.RequestException as e:
        click.echo(f"Error during API request: {e}")

@main.command()
def Logout():
    """Logout from Vijil CLI."""
    remove_config()
    click.echo("Logout done")

main.add_command(run)
main.add_command(status)
main.add_command(stop)
main.add_command(delete)
main.add_command(download)
main.add_command(list)
main.add_command(integrations)
main.add_command(tokens)
main.add_command(logs)

if __name__ == '__main__':
    main()
