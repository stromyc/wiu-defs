import json
import sys

def diff(file):
    with open(file) as f:
        data = json.load(f)

    waysides = data["waysides"]
    print(f"Total waysides: {len(waysides)}\n")

    for k in sorted(waysides.keys(), key=lambda x: int(x) if x.isdigit() else x):
        print(k)

if __name__ == "__main__":
    diff(sys.argv[1])
