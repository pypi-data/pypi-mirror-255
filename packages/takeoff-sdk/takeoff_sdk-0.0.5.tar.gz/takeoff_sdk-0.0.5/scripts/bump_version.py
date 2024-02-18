"""This script is used to bump the version of the package. pyproject.toml is used to store the version."""
import sys
import toml


def read_version():
    with open("pyproject.toml", "r") as file:
        data = toml.load(file)
    return data["project"]["version"]


def write_version(new_version):
    # Read the content of the file
    with open("pyproject.toml", "r") as file:
        content = file.readlines()

    # Find and update the version line
    for i, line in enumerate(content):
        if line.startswith("version = "):
            content[i] = f'version = "{new_version}"\n'
            break

    # Write the updated content back to the file
    with open("pyproject.toml", "w") as file:
        file.writelines(content)


def bump_version(version_part):
    major, minor, patch = map(int, read_version().split("."))
    if version_part == "major":
        major += 1
        minor = 0
        patch = 0
    elif version_part == "minor":
        minor += 1
        patch = 0
    elif version_part == "patch":
        patch += 1
    return f"{major}.{minor}.{patch}"


if __name__ == "__main__":
    part = sys.argv[1] if len(sys.argv) > 1 else "patch"
    new_version = bump_version(part)
    write_version(new_version)
    print(f"Version updated to: {new_version}")
