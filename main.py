#!/usr/bin/env python3

import os
import pathlib
import stat
import subprocess
import sys


PYTHON_SHEBANG = "#!/usr/bin/env python3\n"


def get_file_type(path: pathlib.Path) -> str:
    """Identify the type of executable."""

    try:
        result = subprocess.run(
            ["file", "--brief", "--mime-type", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )

        mime = result.stdout.strip()

    except (subprocess.CalledProcessError, FileNotFoundError):
        mime = ""

    if mime == "application/x-pie-executable":
        return "binary"

    if mime == "application/x-executable":
        return "binary"

    if mime in {
        "text/x-python",
        "text/x-script.python",
    }:
        return "python"

    if mime.startswith("text/"):
        return "script"

    return "unknown"


def has_shebang(path: pathlib.Path) -> bool:
    """Check whether the file already has a shebang."""

    try:
        with path.open("rb") as f:
            first_line = f.readline(256)

        return first_line.startswith(b"#!")

    except OSError:
        return False


def add_python_shebang(path: pathlib.Path):
    """Add a Python shebang if the file is Python and doesn't have one."""

    if has_shebang(path):
        print(f"ℹ️  Shebang already exists: {path.name}")
        return

    print(f"🐍 Adding Python shebang to '{path.name}'...")

    try:
        content = path.read_text()
        path.write_text(PYTHON_SHEBANG + content)

    except UnicodeDecodeError:
        print(f"❌ '{path.name}' does not appear to be text.")
        sys.exit(1)


def ensure_executable(path: pathlib.Path):
    """Make the file executable without destroying existing permissions."""

    mode = path.stat().st_mode

    if not (mode & stat.S_IXUSR):
        path.chmod(mode | stat.S_IXUSR)


def deploy(source_script: str, command_name: str):

    source_path = pathlib.Path(source_script).expanduser().resolve()
    target_dir = pathlib.Path.home() / ".local" / "bin"
    target_path = target_dir / command_name

    # ---------------------------------------------------------
    # Validate source
    # ---------------------------------------------------------

    if not source_path.exists():
        print(f"❌ Source does not exist: {source_path}")
        sys.exit(1)

    if not source_path.is_file():
        print(f"❌ Source is not a regular file: {source_path}")
        sys.exit(1)

    # ---------------------------------------------------------
    # Detect file type
    # ---------------------------------------------------------

    file_type = get_file_type(source_path)

    print(f"🔍 Detected: {file_type}")
    print(f"   Source: {source_path}")

    # ---------------------------------------------------------
    # Handle file appropriately
    # ---------------------------------------------------------

    if file_type == "python":

        if not has_shebang(source_path):
            add_python_shebang(source_path)

        ensure_executable(source_path)

    elif file_type == "binary":

        print("⚙️  Binary detected — leaving file untouched.")
        ensure_executable(source_path)

    elif file_type == "script":

        if not has_shebang(source_path):
            print(
                f"⚠️  '{source_path.name}' is a script but has no shebang."
            )
            print("   Not modifying it automatically.")

        ensure_executable(source_path)

    else:

        print(
            f"⚠️  Could not confidently identify '{source_path.name}'."
        )

        if not has_shebang(source_path):
            print("   No modifications made.")

        ensure_executable(source_path)

    # ---------------------------------------------------------
    # Create ~/.local/bin
    # ---------------------------------------------------------

    target_dir.mkdir(parents=True, exist_ok=True)

    # ---------------------------------------------------------
    # Replace existing deployment
    # ---------------------------------------------------------

    if target_path.exists() or target_path.is_symlink():

        print(f"♻️  Replacing existing command: {target_path}")

        target_path.unlink()

    # ---------------------------------------------------------
    # Create symlink
    # ---------------------------------------------------------

    target_path.symlink_to(source_path)

    print()
    print(f"✅ Deployed '{source_path.name}'")
    print(f"   Command : {command_name}")
    print(f"   Target  : {target_path}")
    print(f"   Source  : {source_path}")


def main():

    if len(sys.argv) != 3:

        print(
            f"Usage: {sys.argv[0]} <script_or_binary> <command_name>"
        )

        print()
        print("Examples:")
        print(f"  {sys.argv[0]} main.py ocr-last")
        print(f"  {sys.argv[0]} myscript.sh myscript")
        print(f"  {sys.argv[0]} ./mybinary mybinary")

        sys.exit(1)

    deploy(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
