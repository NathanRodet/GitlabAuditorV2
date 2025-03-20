import os
import re
import requests
from rich import print

PRIVATE_TOKEN_HEADER = "PRIVATE-TOKEN"
MIN_ACCESS_LEVEL_GUEST = "10"
GITLAB_API_PATH = "/api/v4"

class Group:
  def __init__(self, id, name):
    self.id = id
    self.name = name

class Project:
  def __init__(self, id, name):
    self.id = id
    self.name = name

class Job:
  def __init__(self, id):
    self.id = id


def fetch_groups(token, url):
  groups = []
  page = 1
  
  while True:
    response = requests.get(
      f"{url}/groups",
      headers={PRIVATE_TOKEN_HEADER: token},
      params={
        "all_available": "true",
        "per_page": "100",
        "page": str(page),
        "min_access_level": MIN_ACCESS_LEVEL_GUEST,
        "include_subgroups": "true"
      }
    )
    response.raise_for_status()
    data = response.json()
    groups.extend([Group(g["id"], g["name"]) for g in data])
    
    next_page = response.headers.get("x-next-page")
    if not next_page or len(data) < 100:
      break
    page = int(next_page)
  
  print(f"[bold blue]Fetched {len(groups)} groups.[/bold blue]")
  return groups


def fetch_projects_from_groups(token, url, groups):
  projects = []
  
  for group in groups:
    projects.extend(fetch_projects_for_single_group(token, url, group))
  
  print(f"[bold blue]Fetched {len(projects)} projects across all groups.[/bold blue]")
  return projects


def fetch_projects_for_single_group(token, url, group):
  projects = []
  page = 1
  
  while True:
    response = requests.get(
      f"{url}/groups/{group.id}/projects",
      headers={PRIVATE_TOKEN_HEADER: token},
      params={
        "all_available": "true",
        "per_page": "100",
        "page": str(page),
        "min_access_level": MIN_ACCESS_LEVEL_GUEST,
        "include_subgroups": "true"
      }
    )
    response.raise_for_status()
    data = response.json()
    projects.extend([Project(p["id"], p["name"]) for p in data])
    
    next_page = response.headers.get("x-next-page")
    if not next_page or len(data) < 100:
      break
    page = int(next_page)
  
  print(f"[bold blue]Fetched {len(projects)} projects for group {group.name}.[/bold blue]")
  return projects


def fetch_jobs_for_single_project(token, url, project):
  jobs = []
  page = 1
  
  while True:
    response = requests.get(
      f"{url}/projects/{project.id}/jobs",
      headers={PRIVATE_TOKEN_HEADER: token},
      params={
        "per_page": "100",
        "page": str(page),
        "scope[]": ["success", "failed", "canceled"]
      }
    )
    response.raise_for_status()
    data = response.json()
    jobs.extend([Job(j["id"]) for j in data])
    
    next_page = response.headers.get("x-next-page")
    if not next_page or len(data) < 100:
      break
    page = int(next_page)
  
  print(f"[bold blue]Fetched {len(jobs)} jobs for project {project.name}.[/bold blue]")
  return jobs


def clean_ansi_codes(trace):
  return re.sub(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])", "", trace)


def fetch_job_trace(token, url, project_id, job_id):
  response = requests.get(
    f"{url}/projects/{project_id}/jobs/{job_id}/trace",
    headers={PRIVATE_TOKEN_HEADER: token}
  )
  response.raise_for_status()
  return response.text


def fetch_job_traces_for_projects(token, url, projects):
  os.makedirs("results/log_traces", exist_ok=True)
  print("[bold blue]Starting to fetch job traces...[/bold blue]")
  
  for project in projects:
    jobs = fetch_jobs_for_single_project(token, url, project)
    project_dir = f"results/log_traces/{project.name.replace('/', '_')}"
    os.makedirs(project_dir, exist_ok=True)
    
    for job in jobs:
      try:
        trace = fetch_job_trace(token, url, project.id, job.id)
        clean_trace = clean_ansi_codes(trace)
        with open(f"{project_dir}/{job.id}.txt", "w", encoding="utf-8", errors="replace") as file:
          file.write(clean_trace)
        print(f"[blue]  Saved trace for job {job.id}[/blue]")
      except Exception as e:
        print(f"[red]Failed to fetch trace for job {job.id}: {e}[/red]")
