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


def validate_ids(value):
  if not value:
    return []
  
  try:
    ids = [int(id.strip()) for id in value.split(",") if id.strip()]
    if not ids:
      print("No valid IDs provided. Please specify at least one ID.")
      exit(1)
    return ids
  except ValueError:
    print("All IDs must be integers.")
    exit(1)


def validate_token(token):
  if not token.startswith("glpat-"):
    print("[red]Error: Token must start with 'glpat-'[/red]")
    exit(1)
  
  if len(token) != 26:
    print("[red]Error: Token must be 26 characters long.[/red]")
    exit(1)
  
  return token


def validate_url(url):
  if not validators.url(url):
    print("[red]Error: Invalid URL provided.[/red]")
    exit(1)
  
  if not url.startswith(("http://", "https://")):
    print("[red]Error: URL must use HTTP or HTTPS scheme.[/red]")
    exit(1)
  
  return url.rstrip('/')


def validate_scan_type_and_ids(scan_type, ids):
  if scan_type == 'full' and ids:
    print("[red]Error: IDs should not be provided with 'full' scan type.[/red]")
    exit(1)
  
  if scan_type in ('groups', 'projects') and not ids:
    print(f"[red]Error: IDs are required for '{scan_type}' scan type.[/red]")
    exit(1)
    
  parsed_ids = []
  if scan_type in ('groups', 'projects') and ids:
    parsed_ids = validate_ids(ids)
  
  return parsed_ids


def create_args_dict(token, url, scan_type, parsed_ids):
  api_url = urljoin(url, GITLAB_API_PATH)
  
  return {
    "token": token,
    "url": api_url,
    "full_scan": scan_type == 'full',
    "group_ids": parsed_ids if scan_type == 'groups' else [],
    "project_ids": parsed_ids if scan_type == 'projects' else []
  }


@click.command()
@click.option("--gitlab-token", "-t", required=True, help="Your GitLab Personal Access Token (READ ACCESS ONLY).")
@click.option("--instance-url", "-u", required=True, help="The URL of the GitLab instance to be scanned.")
@click.option("--scan-type", "-s", required=True, type=click.Choice(['full', 'groups', 'projects']), 
        help="Specify the scan type: 'full' for entire instance, 'groups' for specific groups, 'projects' for specific projects.")
@click.option("--ids", "-i", help="Comma-separated list of IDs to scan (required for 'groups' or 'projects' scan type).")
def get_args(gitlab_token, instance_url, scan_type, ids):
  print_banner()
  
  token = validate_token(gitlab_token)
  url = validate_url(instance_url)
  parsed_ids = validate_scan_type_and_ids(scan_type, ids)
  
  return create_args_dict(token, url, scan_type, parsed_ids)
