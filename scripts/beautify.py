import json
from pathlib import Path
from collections import OrderedDict

WIU_DIR = Path("wius")

def beautify_file(path):
    data = json.load(open(path, encoding="utf-8"))
    waysides = data.get("waysides")

    if isinstance(waysides, dict):
        # sort waysides by numeric ID when possible
        def keyfunc(k):
            try:
                return int(k)
            except Exception:
                return k

        sorted_ws = OrderedDict(sorted(waysides.items(), key=lambda kv: keyfunc(kv[0])))
        data["waysides"] = sorted_ws

    # Prefer top-level key order: version, description, waysides, then others
    preferred = ["version", "description", "waysides"]
    ordered = OrderedDict()

    for k in preferred:
        if k in data:
            ordered[k] = data.pop(k)

    for k in sorted(data.keys()):
        ordered[k] = data[k]

    with open(path, "w", encoding="utf-8") as f:
        json.dump(ordered, f, indent=2, ensure_ascii=False)


def main():
    json_files = list(WIU_DIR.glob("*.json"))

    for file in json_files:
        print(f"Beautifying {file.name}...")
        beautify_file(file)

    print("Beautify complete.")

if __name__ == "__main__":
    main()
