# deploy_tool 🚀

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/platform-linux-lightgrey.svg)]()

> Seamlessly deploy your Python scripts, shell scripts, and compiled binaries into your `PATH` so they can be executed from anywhere in your terminal.

---

## 📖 Overview

When developing utility scripts or small CLI tools, testing and running them globally usually requires manual work: adding shebangs, making them executable (`chmod +x`), and linking them into a directory in `$PATH` (like `~/.local/bin`).

**`deploy_tool`** automates this entire workflow in a single command. It inspects the file type, ensures the appropriate shebang is present (automatically prepending `#!/usr/bin/env python3` for Python scripts), ensures executable permissions, and symlinks the file to `~/.local/bin/<command_name>` (or your custom directory).

---

## ✨ Features

- 🔍 **Smart File Type Detection**: Accurately recognizes Python scripts, shell scripts, and compiled ELF binaries via extension, file headers, shebang inspection, and MIME detection.
- 🐍 **Automatic Python Shebang Injection**: Automatically injects `#!/usr/bin/env python3` into Python files if missing, ensuring they run as standalone executables.
- 🔒 **Safe Permission Handling**: Ensures user execution bit (`chmod +x`) is set without overwriting existing permission masks.
- 🔗 **Symlink-based Deployment**: Deploys by creating symbolic links into `~/.local/bin/`. Changes made in the source file are immediately active without redeploying.
- ♻️ **Clean Replacement**: Replaces existing broken or old command symlinks seamlessly.
- 🔎 **Dry-Run Mode**: Inspect and verify actions without altering any files or creating symlinks (`--dry-run`).
- 📁 **Configurable Target Directory**: Easily deploy to custom directories using `--target-dir` / `-t`.

---

## 📂 Repository Structure

```text
deploy_tool/
├── deploy_tool/              # Core Python package
│   ├── __init__.py           # Package exports & version
│   ├── cli.py                # Command-line interface & argument parser
│   └── core.py               # Deployment logic & file type detection
├── examples/                 # Sample scripts for demonstration
│   ├── hello_python.py       # Python script without shebang
│   └── hello_script.sh       # Standard shell script
├── tests/                    # Automated unit & integration tests
│   ├── __init__.py
│   └── test_deploy_tool.py   # Complete test suite
├── .gitignore                # Git ignore patterns
├── LICENSE                   # MIT License
├── main.py                   # Standalone CLI entry point
├── pyproject.toml            # Modern PEP 621 packaging metadata
└── README.md                 # Project documentation
```

---

## ⚡ Quick Start

### Prerequisites

Ensure `~/.local/bin` is in your shell `PATH`. If it isn't already, add this line to your `~/.bashrc` or `~/.zshrc`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

Then reload your shell configuration:

```bash
source ~/.bashrc  # or source ~/.zshrc
```

---

## 📦 Installation

### Option 1: Standalone / Direct Usage

No installation required! Clone the repository and execute directly:

```bash
git clone https://github.com/NonLaHu/deploy_tool.git
cd deploy_tool
./main.py --help
```

You can even self-deploy `deploy_tool` so it is globally available:

```bash
./main.py main.py deploy-tool
```

### Option 2: Pip Install (Editable Mode)

Install as a CLI package into your active Python environment:

```bash
pip install -e .
```

Now `deploy-tool` is directly callable:

```bash
deploy-tool --help
```

---

## 🛠️ Usage & Examples

### Command Syntax

```bash
deploy-tool [-h] [-t TARGET_DIR] [-n] [-v] <source_script> <command_name>
```

#### Arguments & Options

| Argument / Option | Description |
| :--- | :--- |
| `source_script` | Path to the script or binary to deploy |
| `command_name` | The name of the executable command to create in your PATH |
| `-t, --target-dir` | Custom installation directory (default: `~/.local/bin`) |
| `-n, --dry-run` | Preview deployment actions without making any changes |
| `-v, --version` | Display program version |
| `-h, --help` | Display help message and exit |

---

### Examples

#### 1. Deploying a Python Script
If you have a Python script `myscript.py` without a shebang:

```bash
deploy-tool examples/hello_python.py hello-py
```
Output:
```text
🔍 Detected file type: python
   Source: /path/to/deploy_tool/examples/hello_python.py
🐍 Adding Python shebang to 'hello_python.py'...

✅ Successfully deployed 'hello_python.py'
   Command : hello-py
   Target  : /home/user/.local/bin/hello-py
   Source  : /path/to/deploy_tool/examples/hello_python.py
```
Now you can simply run:
```bash
hello-py
```

#### 2. Deploying a Shell Script
```bash
deploy-tool examples/hello_script.sh hello-sh
```
Now run:
```bash
hello-sh
```

#### 3. Deploying a Compiled Binary
```bash
deploy-tool ./mybinary mybinary
```

#### 4. Dry Run (Preview)
```bash
deploy-tool examples/hello_python.py test-cmd --dry-run
```
Output:
```text
🔍 Detected file type: python
   Source: /path/to/deploy_tool/examples/hello_python.py
🔎 Dry run mode enabled — no changes will be made.
   Target: /home/user/.local/bin/test-cmd
```

#### 5. Custom Target Directory
```bash
deploy-tool myscript.py mytool -t /usr/local/bin
```

---

## 🧪 Running Tests

The test suite covers file type detection, shebang injection, permission management, symlinking, overwrite handling, dry-run mode, and error handling.

Run tests using Python's built-in `unittest`:

```bash
python3 -m unittest discover tests
```

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
