"""
Unit and integration tests for deploy_tool.
"""

import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

from deploy_tool.cli import main as cli_main
from deploy_tool.core import (
    PYTHON_SHEBANG,
    DeployError,
    add_python_shebang,
    deploy,
    ensure_executable,
    get_file_type,
    has_shebang,
)


class TestDeployTool(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.test_root = pathlib.Path(self.temp_dir.name)
        self.target_dir = self.test_root / "bin"

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_has_shebang(self):
        script_with_shebang = self.test_root / "with_shebang.sh"
        script_with_shebang.write_text("#!/bin/bash\necho hi\n")
        self.assertTrue(has_shebang(script_with_shebang))

        script_without_shebang = self.test_root / "no_shebang.txt"
        script_without_shebang.write_text("echo hi\n")
        self.assertFalse(has_shebang(script_without_shebang))

        empty_file = self.test_root / "empty.txt"
        empty_file.write_text("")
        self.assertFalse(has_shebang(empty_file))

    def test_get_file_type_python(self):
        py_file = self.test_root / "myscript.py"
        py_file.write_text("print('hello')\n")
        self.assertEqual(get_file_type(py_file), "python")

        pyw_file = self.test_root / "myscript.pyw"
        pyw_file.write_text("print('hello')\n")
        self.assertEqual(get_file_type(pyw_file), "python")

        # Python script without extension but with python shebang
        custom_py = self.test_root / "custom_cli"
        custom_py.write_text("#!/usr/bin/env python3\nprint('hello')\n")
        self.assertEqual(get_file_type(custom_py), "python")

    def test_get_file_type_script(self):
        sh_file = self.test_root / "myscript.sh"
        sh_file.write_text("echo 'hello'\n")
        self.assertEqual(get_file_type(sh_file), "script")

        bash_file = self.test_root / "custom_bash"
        bash_file.write_text("#!/bin/bash\necho 'hello'\n")
        self.assertEqual(get_file_type(bash_file), "script")

    def test_get_file_type_binary(self):
        elf_file = self.test_root / "dummy_binary"
        elf_file.write_bytes(b"\x7fELF\x02\x01\x01\x00")
        self.assertEqual(get_file_type(elf_file), "binary")

    def test_add_python_shebang(self):
        py_file = self.test_root / "script.py"
        py_file.write_text("print('test')\n")

        added = add_python_shebang(py_file)
        self.assertTrue(added)
        self.assertTrue(py_file.read_text().startswith(PYTHON_SHEBANG))

        # Adding shebang again should be a no-op
        added_again = add_python_shebang(py_file)
        self.assertFalse(added_again)
        self.assertEqual(py_file.read_text().count(PYTHON_SHEBANG.strip()), 1)

    def test_ensure_executable(self):
        script = self.test_root / "run.sh"
        script.write_text("echo test\n")
        script.chmod(0o644)

        ensure_executable(script)
        mode = script.stat().st_mode
        self.assertTrue(bool(mode & stat.S_IXUSR))

    def test_deploy_python_script_e2e(self):
        py_file = self.test_root / "hello.py"
        py_file.write_text("print('Deploy Success!')\n")

        target_cmd = deploy(
            source_script=py_file,
            command_name="test-hello",
            target_dir=self.target_dir,
        )

        self.assertTrue(target_cmd.exists())
        self.assertTrue(target_cmd.is_symlink())
        self.assertEqual(target_cmd.resolve(), py_file.resolve())

        # Check shebang was added
        self.assertTrue(has_shebang(py_file))
        # Check source is executable
        self.assertTrue(bool(py_file.stat().st_mode & stat.S_IXUSR))

        # Test executing the target command directly
        proc = subprocess.run(
            [str(target_cmd)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "Deploy Success!")

    def test_deploy_shell_script_e2e(self):
        sh_file = self.test_root / "hello.sh"
        sh_file.write_text("#!/bin/sh\necho 'Shell Success!'\n")

        target_cmd = deploy(
            source_script=sh_file,
            command_name="test-sh",
            target_dir=self.target_dir,
        )

        self.assertTrue(target_cmd.is_symlink())
        proc = subprocess.run(
            [str(target_cmd)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "Shell Success!")

    def test_deploy_replacement(self):
        v1_file = self.test_root / "v1.py"
        v1_file.write_text("print('v1')\n")
        deploy(v1_file, "version-cmd", target_dir=self.target_dir)

        target_cmd = self.target_dir / "version-cmd"
        self.assertEqual(target_cmd.resolve(), v1_file.resolve())

        v2_file = self.test_root / "v2.py"
        v2_file.write_text("print('v2')\n")
        deploy(v2_file, "version-cmd", target_dir=self.target_dir)

        self.assertEqual(target_cmd.resolve(), v2_file.resolve())
        proc = subprocess.run([str(target_cmd)], capture_output=True, text=True)
        self.assertEqual(proc.stdout.strip(), "v2")

    def test_deploy_dry_run(self):
        py_file = self.test_root / "dry_run.py"
        py_file.write_text("print('dry')\n")

        target_cmd = deploy(
            source_script=py_file,
            command_name="dry-cmd",
            target_dir=self.target_dir,
            dry_run=True,
        )

        # In dry run, target symlink should NOT be created
        self.assertFalse(target_cmd.exists())
        # Source file should not have shebang added
        self.assertFalse(has_shebang(py_file))

    def test_deploy_nonexistent_source(self):
        missing_file = self.test_root / "does_not_exist.py"
        with self.assertRaises(DeployError):
            deploy(missing_file, "missing-cmd", target_dir=self.target_dir)

    def test_cli_execution(self):
        py_file = self.test_root / "cli_test.py"
        py_file.write_text("print('CLI Works!')\n")

        ret = cli_main([
            str(py_file),
            "cli-cmd",
            "--target-dir",
            str(self.target_dir),
        ])
        self.assertEqual(ret, 0)

        target_cmd = self.target_dir / "cli-cmd"
        self.assertTrue(target_cmd.exists())
        proc = subprocess.run([str(target_cmd)], capture_output=True, text=True)
        self.assertEqual(proc.stdout.strip(), "CLI Works!")


if __name__ == "__main__":
    unittest.main()
