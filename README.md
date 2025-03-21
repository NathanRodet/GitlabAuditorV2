# GitlabAuditorV2

A tool aiming to find secrets in your gitlab instance pipelines logs. But in Python.

## Run the tool

```bash
# Install deps
python -m pip install -r requirements.txt

# Run the tool
python main.py -t <Gitlab-Access-Token> -u <Gitlab URL> -scan-type full
python main.py -t <Gitlab-Access-Token> -u <Gitlab URL> -scan-type groups --ids 1,2,3
python main.py -t <Gitlab-Access-Token> -u <Gitlab URL> -scan-type projects --ids 1,2,3
```

> **Note:** This tool only needs **read_api** rights on Gitlab Personal access token.

## Secret Detection with Gitleaks

### [Get Gitleaks from official repository](https://github.com/gitleaks/gitleaks/releases)

```bash
# Run Gitleak
./gitleaks detect --source "<path-to-results>" --report-format json --report-path gitleaks_results.json --no-git
```

## RoadMap

- [x] Full Scan
- [x] Secret detection
- [x] Groups Scan
- [x] Projects Scan
