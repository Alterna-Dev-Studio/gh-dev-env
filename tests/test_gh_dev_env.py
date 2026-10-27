"""Exercise gh-dev-env with a fake gh and git, so no network or GitHub account is used.

Run with: python3 -m unittest discover -s tests
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent.parent


class GhDevEnvTests(unittest.TestCase):
    """Drive gh-dev-env with a fake gh that clones a stub setup, so no network is used."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp)
        self.work = self.tmp / "work"
        self.work.mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.log = self.tmp / "log"
        self.write_tool("gh", """
            echo "gh $*" >> "$LOG"
            dir="${3##*/}"; mkdir -p "$dir/scripts"
            [ -n "${EMPTY_CLONE:-}" ] && exit 0
            printf '#!/bin/sh\\necho "setup $(basename "$PWD") $*" >> "$LOG"\\n' > "$dir/scripts/setup"
            chmod +x "$dir/scripts/setup"
        """)
        self.env = {"HOME": str(self.tmp), "LOG": str(self.log),
                    "PATH": os.pathsep.join([str(self.bin), "/usr/bin", "/bin"])}

    def write_tool(self, name, body):
        tool = self.bin / name
        tool.write_text("#!/bin/sh\n" + "\n".join(line.strip() for line in body.splitlines()) + "\n")
        tool.chmod(0o755)

    def run_new(self, *args):
        return subprocess.run([str(ROOT / "gh-dev-env"), *args], env=self.env, cwd=self.work,
                              stdin=subprocess.DEVNULL, text=True, capture_output=True)

    def test_creates_private_repo_from_template_and_runs_setup_in_clone(self):
        result = self.run_new("me/box", "--skip-taiga-mcp")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines(), [
            "gh repo create me/box --template Alterna-Dev-Studio/dev-env-template --private --clone",
            "setup box --skip-taiga-mcp",
        ])

    def test_default_name_is_my_dev_env(self):
        self.assertEqual(self.run_new().returncode, 0)
        self.assertIn("gh repo create my-dev-env ", self.log.read_text())

    def test_existing_directory_is_refused_before_creating_a_repo(self):
        (self.work / "box").mkdir()
        result = self.run_new("box")
        self.assertEqual(result.returncode, 1)
        self.assertIn("box already exists", result.stderr)
        self.assertFalse(self.log.exists())

    def test_empty_clone_is_pulled_until_template_files_arrive(self):
        self.env["EMPTY_CLONE"] = "1"
        self.write_tool("git", """
            echo "git $*" >> "$LOG"
            printf '#!/bin/sh\\necho "setup $(basename "$PWD")" >> "$LOG"\\n' > "$2/scripts/setup"
            chmod +x "$2/scripts/setup"
        """)
        result = self.run_new("box")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(self.log.read_text().splitlines()[1:],
                         ["git -C box pull --quiet origin HEAD", "setup box"])



if __name__ == "__main__":
    unittest.main()
