import cli
import scans.full as full_scan
import scans.groups as groups_scan
import scans.projects as projects_scan
from rich import print
import os
import shutil

BASE_RESULTS_DIR = "results/log_traces"

def remove_old_results():
  if os.path.exists(BASE_RESULTS_DIR):
    shutil.rmtree(BASE_RESULTS_DIR)
    print(f"[blue]Removed existing results directory: {BASE_RESULTS_DIR}[/blue]")
  
  os.makedirs(BASE_RESULTS_DIR, exist_ok=True)

def main():
  remove_old_results()
  args = cli.get_args(standalone_mode=False)

  token = args["token"]
  url = args["url"]
  full_scan_enabled = args["full_scan"]
  group_ids = args["group_ids"]
  project_ids = args["project_ids"]
  
  if not token or not url:
    print("[bold red]Error: Token and URL are required[/bold red]")
    return 1

  print("[bold blue]Configuration:[/bold blue]")
  print(f"  [blue]Instance URL: {url}[/blue]")
  print(f"  [blue]Gitlab Token: {token[:-16] + '*' * 16}[/blue]")

  try:
    match True:
      case _ if full_scan_enabled:
        print("[blue]  Performing full scan of all groups and projects[/blue]")
        projects = full_scan.run(token, url)
      case _ if group_ids:
        print(f"[blue]  Scanning specific groups: {group_ids}[/blue]")
        projects = groups_scan.run(token, url, group_ids)
      case _ if project_ids:
        print(f"[blue]  Scanning specific projects: {project_ids}[/blue]")
        projects = projects_scan.run(token, url, project_ids)
      case _:
        print("[bold red]No scan type specified[/bold red]")
        return 1
    
    if not project_ids:
      full_scan.fetch_job_traces_for_projects(token, url, projects)
    print("\n[bold blue]Finished fetching job traces.[/bold blue]")
    
  except Exception as e:
    print(f"[bold red]Error during scan: {e}[/bold red]")
    return 1

  print("[bold green]Finished scanning, results saved at /results.[/bold green]")
  return 0


if __name__ == "__main__":
  exit(main())
