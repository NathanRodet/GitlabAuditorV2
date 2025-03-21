from rich import print
from scans.full import MIN_ACCESS_LEVEL_GUEST, Project, fetch_paginated_data

def fetch_projects_for_single_group(token, url, group_id):
  base_url = f"{url}/groups/{group_id}/projects"
  params = {
    "all_available": "true",
    "min_access_level": MIN_ACCESS_LEVEL_GUEST,
    "include_subgroups": "true"
  }
  
  data = fetch_paginated_data(base_url, token, params)
  projects = [Project(p["id"], p["name"]) for p in data]
  
  print(f"[blue]  Fetched {len(projects)} projects for group {group_id}.[/blue]")
  return projects


def fetch_projects_from_groups(token, url, group_ids):
  projects = []
  
  for group_id in group_ids:
    projects.extend(fetch_projects_for_single_group(token, url, group_id))
  
  print(f"[bold blue]Fetched {len(projects)} projects across all groups.[/bold blue]")
  return projects


def run(token, url, group_ids):
  try:
    projects = fetch_projects_from_groups(token, url, group_ids)
    if not projects:
      return 0
    return projects
  except Exception as e:
    print(f"[bold red]Error fetching projects: {e}[/bold red]")
    return 1
