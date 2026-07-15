import os
import pathlib
import sys

def deploy(source_script: str, new_command_name: str):
    # 1. Expand paths
    source_path = pathlib.Path(source_script).resolve()
    target_dir = pathlib.Path.home() / ".local/bin"
    target_path = target_dir / new_command_name

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
        print("Usage: python deploy.py <script_path> <new_command_name>")
    else:
        deploy(sys.argv[1], sys.argv[2])
