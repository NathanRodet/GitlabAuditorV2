import cli
import scan
from rich import print


def main():
  args = cli.get_args(standalone_mode=False)

  token = args["token"]
  url = args["url"]
  
  if not token or not url:
    print("[bold red]Error: Token and URL are required[/bold red]")
    return 1

  print("[bold blue]Configuration:[/bold blue]")
  print(f"  [blue]Instance URL: {url}[/blue]")
  print(f"  [blue]Gitlab Token: {token[:-16] + '*' * 16 }[/blue]")

  try:
    groups = scan.fetch_groups(token, url)
    if not groups:
      print("[bold yellow]No groups found[/bold yellow]")
      return 0
  except Exception as e:
    print(f"[bold red]Error fetching groups: {e}[/bold red]")
    return 1

  try:
    projects = scan.fetch_projects_from_groups(token, url, groups)
    if not projects:
      print("[bold yellow]No projects found[/bold yellow]")
      return 0
  except Exception as e:
    print(f"[bold red]Error fetching projects: {e}[/bold red]")
    return 1

  try:
    scan.fetch_job_traces_for_projects(token, url, projects)
    print("\n[bold blue]Finished fetching job traces.[/bold blue]")
  except Exception as e:
    print(f"[bold red]Error fetching job traces: {e}[/bold red]")
    return 1

  print("[bold green]Finished scanning, results saved at /results.[/bold green]")
  return 0


if __name__ == "__main__":
  exit(main())
