"""
CLI interface for deploy_tool.
"""

import argparse
import sys
from typing import List, Optional

from deploy_tool import __version__
from deploy_tool.core import DeployError, deploy


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deploy-tool",
        description="Deploy Python scripts, shell scripts, or compiled binaries into your PATH (~/.local/bin) as global commands.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  deploy-tool script.py mytool            # Deploy Python script, adding shebang if needed
  deploy-tool myscript.sh myscript        # Deploy shell script
  deploy-tool ./mybinary mybinary         # Deploy compiled binary
  deploy-tool script.py mytool --dry-run  # Simulate deployment without changes
  deploy-tool script.py mytool -t ~/bin   # Deploy to custom directory
""",
    )

    parser.add_argument(
        "source_script",
        help="Path to the script or binary to deploy",
    )
    parser.add_argument(
        "command_name",
        help="Name of the executable command to create in PATH",
    )
    parser.add_argument(
        "-t",
        "--target-dir",
        default=None,
        help="Custom target directory (default: ~/.local/bin)",
    )
    parser.add_argument(
        "-n",
        "--dry-run",
        action="store_true",
        help="Preview deployment actions without modifying files or creating symlinks",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        deploy(
            source_script=args.source_script,
            command_name=args.command_name,
            target_dir=args.target_dir,
            dry_run=args.dry_run,
        )
        return 0
    except DeployError as err:
        print(f"❌ Error: {err}", file=sys.stderr)
        return 1
    except Exception as err:
        print(f"❌ Unexpected error: {err}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
