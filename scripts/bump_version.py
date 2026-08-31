import json
import re
from pathlib import Path

WIUS_DIR = Path("wius")

SEMVER_RE = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")


def bump_version_value(v):
    if v is None:
        return "1"
    if isinstance(v, int):
        return str(v + 1)
    if isinstance(v, str):
        m = SEMVER_RE.match(v.strip())
        if m:
            major, minor, patch = map(int, m.groups())
            patch += 1
            return f"{major}.{minor}.{patch}"
        if v.isdigit():
            return str(int(v) + 1)
        # try to extract trailing number
        nums = re.findall(r"(\d+)$", v)
        if nums:
            return v[: -len(nums[-1])] + str(int(nums[-1]) + 1)
        return v + "-1"
    # fallback
    return "1"


def main():
    changed = []
    for file in sorted(WIUS_DIR.glob("*.json")):
        data = json.load(open(file, encoding="utf-8"))
        old = data.get("version")
        new = bump_version_value(old)
        if old != new:
            data["version"] = new
            with open(file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            changed.append((file.name, old, new))
            print(f"Bumped {file.name}: {old} -> {new}")
        else:
            print(f"No change for {file.name} (version {old})")

    if changed:
        print("Updated versions for:")
        for name, old, new in changed:
            print(f" - {name}: {old} -> {new}")
    else:
        print("No versions changed.")


if __name__ == '__main__':
    main()
