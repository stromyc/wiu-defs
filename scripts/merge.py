import json
from pathlib import Path

WIU_DIR = Path("wius")

def load_json(path):
    with open(path, "r") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2, sort_keys=True)

def merge(master, local):
    master_ws = master["waysides"]
    local_ws = local["waysides"]

    # Add missing local → master
    for k, v in local_ws.items():
        master_ws.setdefault(k, v)

    # Add missing master → local
    for k, v in master_ws.items():
        local_ws.setdefault(k, v)

    return master

def main():
    json_files = list(WIU_DIR.glob("*.json"))

    for file in json_files:
        print(f"Merging {file.name}...")

        local = load_json(file)
        master = load_json(file)

        merged = merge(master, local)
        save_json(file, merged)

    print("All merges complete.")

if __name__ == "__main__":
    main()
