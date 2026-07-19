#!/usr/bin/env python3
import os
import pathlib
import sys

def add_shebang_if_missing(file_path: pathlib.Path):
    shebang = "#!/usr/bin/env python3\n"
    with open(file_path, 'r') as f:
        lines = f.readlines()

    # Check if the first line is already a shebang
    if not lines or not lines[0].startswith("#!"):
        print(f"ℹ️  Adding shebang to '{file_path.name}'...")
        with open(file_path, 'w') as f:
            f.write(shebang)
            f.writelines(lines)

def deploy(source_script: str, new_command_name: str):
    # 1. Expand paths
    source_path = pathlib.Path(source_script).resolve()
    target_dir = pathlib.Path.home() / ".local/bin"
    target_path = target_dir / new_command_name

    # 0. Ensure script has a shebang
    add_shebang_if_missing(source_path)

    # 2. Ensure bin directory exists
    target_dir.mkdir(parents=True, exist_ok=True)

    # 3. Make source executable
    os.chmod(source_path, 0o755)

    # 4. Create symlink (remove existing if necessary)
    if target_path.exists() or target_path.is_symlink():
        target_path.unlink()

    os.symlink(source_path, target_path)

    print(f"✅ Deployed '{source_script}' as command: '{new_command_name}'")
    print(f"   Location: {target_path}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: deploy <script_path> <new_command_name>")
    else:
        deploy(sys.argv[1], sys.argv[2])
