# ITCMon WIU Configurations 
Master WIU Wayside Configuration Database

This repository stores master WIU wayside JSON files for ATCS/railroad telemetry decoding. Multiple contributors may update these files, and this repo provides tools to safely merge changes, prevent duplicates, validate structure, and maintain consistency.

## Repository Structure

```
wius/           # Master JSON files (e.g. 103xxx.json, 105xxx.json)
scripts/         # Merge, diff, and validation tools
schema/          # JSON schema for validation
.github/         # GitHub Actions automation (workflows)
```

## Contributor Workflow

### Editing an Existing WIU File
1. `git pull`
2. Edit the existing `wius/<number>.json` file you are updating (for example, `wius/103xxx.json` or `wius/105xxx.json`)
3. Optional local sanity check: `python scripts/validate.py`
4. Stage your changes: `git add wius/<number>.json` (stages new or modified files)
5. `git commit`
6. `git push`
7. Open or update a pull request

### Adding a New WIU File
1. `git pull`
2. Create a new `wius/<number>.json` file using the approved format (for example, `wius/103xxx.json` or `wius/105xxx.json`)
3. Optional local sanity check: `python scripts/validate.py`
4. Stage your new file: `git add wius/<number>.json` (stages new or modified files)
5. `git commit`
6. `git push`
7. Open or update a pull request

## GitHub Action
Once the pull request is reviewed and merged, the GitHub Action automatically runs the beautify, merge, validation, and version-bump workflow and updates the master JSON files.

Note: The workflow auto-increments the top-level `version` value in each `wius/*.json` on merge. Do not manually edit the `version` field — CI will manage it.

## Running validate.py locally
For a quick local validation (Windows PowerShell example):

1. Open PowerShell at the repository root.
2. (Optional) Create and activate a virtual environment:
   `python -m venv .venv`
   `.\.venv\Scripts\Activate.ps1`
3. Install the dependency:
   `pip install jsonschema`
4. Run the validator against all files in `wius/`:
   `python scripts\validate.py`

If you prefer not to use a virtual environment, install jsonschema for your user and run the script:

   `pip install --user jsonschema`
   `python scripts\validate.py`

The script validates every `wius/*.json` file and prints `OK` for success or `ERROR` with a message for each failure.

## Rules
- Edit or create only WIU/*.json files 
- Optional local validation is allowed before committing 
- Do not create duplicate wayside IDs 
- Do not reorder arrays 
- Do not delete fields unless intentional 
