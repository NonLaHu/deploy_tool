"""
Core deployment logic for deploy_tool.
"""

import os
import pathlib
import stat
import subprocess
import sys
from typing import Optional, Union

PYTHON_SHEBANG = "#!/usr/bin/env python3\n"
DEFAULT_TARGET_DIR = pathlib.Path.home() / ".local" / "bin"


class DeployError(Exception):
    """Custom exception raised when deployment fails."""
    pass


def has_shebang(path: pathlib.Path) -> bool:
    """Check whether the file begins with a shebang (#!)."""
    try:
        with path.open("rb") as f:
            first_line = f.readline(256)
        return first_line.startswith(b"#!")
    except OSError:
        return False


def get_file_type(path: pathlib.Path) -> str:
    """
    Identify the type of executable: 'python', 'script', 'binary', or 'unknown'.

    Detection checks:
    1. Python extension (.py, .pyw) -> 'python'
    2. Shebang inspection -> 'python' or 'script'
    3. Shell script extensions (.sh, .bash, .zsh, .fish) -> 'script'
    4. ELF binary magic bytes -> 'binary'
    5. Fallback to `file` system utility
    """
    # 1. Quick extension check
    suffix = path.suffix.lower()
    if suffix in {".py", ".pyw"}:
        return "python"
    if suffix in {".sh", ".bash", ".zsh", ".fish"}:
        return "script"

    # 2. Shebang inspection
    try:
        with path.open("rb") as f:
            first_line = f.readline(256).decode("utf-8", errors="ignore").strip()
            if first_line.startswith("#!"):
                if "python" in first_line:
                    return "python"
                return "script"
    except OSError:
        pass

    # 3. Binary header check (ELF magic \x7fELF on Linux)
    try:
        with path.open("rb") as f:
            header = f.read(4)
            if header == b"\x7fELF":
                return "binary"
    except OSError:
        pass

    # 4. Fallback to `file` system utility if available
    try:
        result = subprocess.run(
            ["file", "--brief", "--mime-type", str(path)],
            capture_output=True,
            text=True,
            check=True,
        )
        mime = result.stdout.strip()

        if mime in {"application/x-pie-executable", "application/x-executable", "application/x-sharedlib"}:
            return "binary"

        if mime in {"text/x-python", "text/x-script.python"}:
            return "python"

        if mime.startswith("text/"):
            return "script"

    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    return "unknown"


def add_python_shebang(path: pathlib.Path) -> bool:
    """
    Add a Python shebang if the file doesn't already have one.
    Returns True if shebang was added, False if it already had one.
    """
    if has_shebang(path):
        print(f"ℹ️  Shebang already exists: {path.name}")
        return False

    print(f"🐍 Adding Python shebang to '{path.name}'...")
    try:
        content = path.read_text(encoding="utf-8")
        path.write_text(PYTHON_SHEBANG + content, encoding="utf-8")
        return True
    except UnicodeDecodeError:
        raise DeployError(f"'{path.name}' does not appear to be valid text.")


def ensure_executable(path: pathlib.Path) -> None:
    """Make the file executable by user (and group/others if readable)."""
    mode = path.stat().st_mode
    new_mode = mode | stat.S_IXUSR
    if mode & stat.S_IRGRP:
        new_mode |= stat.S_IXGRP
    if mode & stat.S_IROTH:
        new_mode |= stat.S_IXOTH
    if mode != new_mode:
        path.chmod(new_mode)


def deploy(
    source_script: Union[str, pathlib.Path],
    command_name: str,
    target_dir: Optional[Union[str, pathlib.Path]] = None,
    dry_run: bool = False,
) -> pathlib.Path:
    """
    Deploy a script or binary as a global command.

    Args:
        source_script: Path to source file or binary.
        command_name: Name of the command to create in target_dir.
        target_dir: Target directory (defaults to ~/.local/bin).
        dry_run: If True, inspect and report actions without making changes.

    Returns:
        pathlib.Path: The path to the symlinked target command.
    """
    source_path = pathlib.Path(source_script).expanduser().resolve()
    dest_dir = (pathlib.Path(target_dir).expanduser().resolve()
                if target_dir else DEFAULT_TARGET_DIR)
    target_path = dest_dir / command_name

    # Validate source
    if not source_path.exists():
        raise DeployError(f"Source file does not exist: {source_path}")

    if not source_path.is_file():
        raise DeployError(f"Source is not a regular file: {source_path}")

    # Detect file type
    file_type = get_file_type(source_path)
    print(f"🔍 Detected file type: {file_type}")
    print(f"   Source: {source_path}")

    if dry_run:
        print("🔎 Dry run mode enabled — no changes will be made.")
        print(f"   Target: {target_path}")
        return target_path

    # Handle file according to type
    if file_type == "python":
        if not has_shebang(source_path):
            add_python_shebang(source_path)
        ensure_executable(source_path)

    elif file_type == "binary":
        print("⚙️  Binary detected — leaving file content untouched.")
        ensure_executable(source_path)

    elif file_type == "script":
        if not has_shebang(source_path):
            print(f"⚠️  '{source_path.name}' is a script but has no shebang.")
            print("   Not modifying content automatically.")
        ensure_executable(source_path)

    else:
        print(f"⚠️  Could not confidently identify '{source_path.name}'.")
        if not has_shebang(source_path):
            print("   No modifications made.")
        ensure_executable(source_path)

    # Ensure target directory exists
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Remove existing deployment if target already exists or is a broken symlink
    if target_path.exists() or target_path.is_symlink():
        print(f"♻️  Replacing existing command: {target_path}")
        target_path.unlink()

    # Create symlink
    target_path.symlink_to(source_path)

    print()
    print(f"✅ Successfully deployed '{source_path.name}'")
    print(f"   Command : {command_name}")
    print(f"   Target  : {target_path}")
    print(f"   Source  : {source_path}")

    return target_path
