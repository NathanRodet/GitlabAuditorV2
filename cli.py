import click
import validators
from rich import print
from rich.text import Text
from urllib.parse import urljoin

GITLAB_API_PATH = "/api/v4"


def print_banner() -> None:
  banner = Text("""
 ██████╗ ██╗████████╗██╗      █████╗ ██████╗      █████╗ ██╗   ██╗██████╗ ██╗████████╗ ██████╗ ██████╗ 
██╔════╝ ██║╚══██╔══╝██║     ██╔══██╗██╔══██╗    ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝██╔═══██╗██╔══██╗
██║  ███╗██║   ██║   ██║     ███████║██████╔╝    ███████║██║   ██║██║  ██║██║   ██║   ██║   ██║██████╔╝
██║   ██║██║   ██║   ██║     ██╔══██║██╔══██╗    ██╔══██║██║   ██║██║  ██║██║   ██║   ██║   ██║██╔══██╗
╚██████╔╝██║   ██║   ███████╗██║  ██║██████╔╝    ██║  ██║╚██████╔╝██████╔╝██║   ██║   ╚██████╔╝██║  ██║
 ╚═════╝ ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═════╝     ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝    ╚═════╝ ╚═╝  ╚═╝
  """, style="bold red")
  print(banner)


@click.command()
@click.option("--gitlab-token", "-t", required=True, help="Your GitLab Personal Access Token (READ ACCESS ONLY).")
@click.option("--instance-url", "-u", required=True, help="The URL of the GitLab instance to be scanned.")
def get_args(gitlab_token, instance_url):
  print_banner()
  
  if not gitlab_token.startswith("glpat-"):
    print("[red]Error: Token must start with 'glpat-'[/red]")
    return None
  
  if len(gitlab_token) != 26:
    print("[red]Error: Token must be 26 characters long.[/red]")
    return None
  

  if not validators.url(instance_url):
    print("[red]Error: Invalid URL provided.[/red]")
    return None
  
  if not instance_url.startswith(("http://", "https://")):
    print("[red]Error: URL must use HTTP or HTTPS scheme.[/red]")
    return None
  
  instance_url = instance_url.rstrip('/')  # Remove trailing slash
  api_url = urljoin(instance_url, GITLAB_API_PATH)
  
  args = {
    "token": gitlab_token,
    "url": api_url
  }
  
  return args

