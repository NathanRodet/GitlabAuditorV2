import os
from rich import print
import requests
from scans.full import Job, clean_ansi_codes, fetch_job_trace, fetch_paginated_data


def fetch_jobs_for_single_project(token, url, project_id):
  base_url = f"{url}/projects/{project_id}/jobs"
  params = {
    "scope[]": ["success", "failed", "canceled"]
  }
  
  data = fetch_paginated_data(base_url, token, params)
  print(f"[blue]  Parsing {len(data)} job records...[/blue]")

  jobs = [Job(j["id"]) for j in data]
  
  print(f"[bold blue]Fetched {len(jobs)} jobs for project id {project_id}.[/bold blue]")
  return jobs
  

def get_project_name(token, url, project_id):
  project_url = f"{url}/projects/{project_id}"
  headers = {"PRIVATE-TOKEN": token}
  
  try:
    response = requests.get(project_url, headers=headers)
    response.raise_for_status()
    project_data = response.json()
    return project_data.get("name", f"Project {project_id}")
  except Exception as e:
    print(f"[orange]Warning: Could not fetch name for project {project_id}: {e}[/orange]")
    return f"Project {project_id}"


def fetch_job_traces_for_projects(token, url, project_ids):
  print("[bold blue]Starting to fetch job traces...[/bold blue]")
  
  for project_id in project_ids:
    project_name = get_project_name(token, url, project_id)
    jobs = fetch_jobs_for_single_project(token, url, project_id)
    
    safe_project_name = project_name.replace('/', '_')
    project_dir = f"results/log_traces/{safe_project_name}"
    os.makedirs(project_dir, exist_ok=True)
    
    if not jobs:
      print(f"[blue]  No trace for jobs in {project_id} project to be saved[/blue]")
      continue
      
    for i, job in enumerate(jobs):
      try:
        trace = fetch_job_trace(token, url, project_id, job.id)
        clean_trace = clean_ansi_codes(trace)
        
        trace_path = f"{project_dir}/{job.id}.txt"
        with open(trace_path, "w", encoding="utf-8", errors="replace") as file:
          file.write(clean_trace)
          
        print(f"\r[blue]  Saved trace for job {job.id} ({i + 1}/{len(jobs)})[/blue]".ljust(80), end="\r")
      except Exception as e:
        print(f"[red]Failed to fetch trace for job {job.id}: {str(e)}[/red]")


def run(token, url, group_ids):
  try:
    fetch_job_traces_for_projects(token, url, group_ids)
    return 0
  except Exception as e:
    print(f"[bold red]Error fetching projects: {e}[/bold red]")
    return 1