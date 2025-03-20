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


def fetch_paginated_data(url, token, params=None):
  if params is None:
    params = {}
  
  all_data = []
  page = 1
  
  while True:
    page_params = {**params, "per_page": "100", "page": str(page)}
    response = requests.get(
      url,
      headers={PRIVATE_TOKEN_HEADER: token},
      params=page_params
    )
    response.raise_for_status()
    data = response.json()
    all_data.extend(data)
    
    next_page = response.headers.get("x-next-page")
    if not next_page or len(data) < 100:
      break
    page = int(next_page)
  
  return all_data


def fetch_groups(token, url):
  base_url = f"{url}/groups"
  params = {
    "all_available": "true",
    "min_access_level": MIN_ACCESS_LEVEL_GUEST,
    "include_subgroups": "true"
  }
  
  data = fetch_paginated_data(base_url, token, params)
  groups = [Group(g["id"], g["name"]) for g in data]
  
  print(f"[bold blue]Fetched {len(groups)} groups.[/bold blue]")
  return groups


def fetch_projects_from_groups(token, url, groups):
  projects = []
  
  for group in groups:
    projects.extend(fetch_projects_for_single_group(token, url, group))
  
  print(f"[bold blue]Fetched {len(projects)} projects across all groups.[/bold blue]")
  return projects


def fetch_projects_for_single_group(token, url, group):
  base_url = f"{url}/groups/{group.id}/projects"
  params = {
    "all_available": "true",
    "min_access_level": MIN_ACCESS_LEVEL_GUEST,
    "include_subgroups": "true"
  }
  
  data = fetch_paginated_data(base_url, token, params)
  projects = [Project(p["id"], p["name"]) for p in data]
  
  print(f"[blue]  Fetched {len(projects)} projects for group {group.name}.[/blue]")
  return projects


def fetch_jobs_for_single_project(token, url, project):
  base_url = f"{url}/projects/{project.id}/jobs"
  params = {
    "scope[]": ["success", "failed", "canceled"]
  }
  
  data = fetch_paginated_data(base_url, token, params)
  jobs = [Job(j["id"]) for j in data]
  
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
  print("[blue] Starting to fetch job traces...[/blue]")
  
  for project in projects:
    jobs = fetch_jobs_for_single_project(token, url, project)
    
    safe_project_name = project.name.replace('/', '_')
    project_dir = f"results/log_traces/{safe_project_name}"
    os.makedirs(project_dir, exist_ok=True)
    
    if not jobs:
      print(f"[blue]  No trace for jobs in {project.name} project to be saved[/blue]")
      continue
      
    for job in jobs:
      try:
        trace = fetch_job_trace(token, url, project.id, job.id)
        clean_trace = clean_ansi_codes(trace)
        
        trace_path = f"{project_dir}/{job.id}.txt"
        with open(trace_path, "w", encoding="utf-8", errors="replace") as file:
          file.write(clean_trace)
          
        print(f"\r[blue]  Saved trace for job {job.id} ({jobs.index(job) + 1}/{len(jobs)})[/blue]".ljust(80), end="\r")
      except Exception as e:
        print(f"[red]Failed to fetch trace for job {job.id}: {str(e)}[/red]")
    