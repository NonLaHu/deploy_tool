"""
deploy_tool: Deploy Python scripts, shell scripts, and binaries to your PATH.
"""

__version__ = "0.1.0"

from deploy_tool.core import (
    DeployError,
    add_python_shebang,
    deploy,
    ensure_executable,
    get_file_type,
    has_shebang,
)

__all__ = [
    "__version__",
    "deploy",
    "get_file_type",
    "has_shebang",
    "add_python_shebang",
    "ensure_executable",
    "DeployError",
]
