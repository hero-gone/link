"""Tests for bash scripts in the repo.

Validates:
  - Script has a valid shebang line
  - Script passes bash syntax check (bash -n)
  - Script uses expected color variable definitions
  - Script contains a select/case menu structure
"""

import pathlib
import subprocess

import pytest


class TestBashScriptSyntax:
    def test_has_shebang(self, bash_script):
        first_line = bash_script.read_text(encoding="utf-8").splitlines()[0]
        assert first_line.startswith("#!"), (
            f"{bash_script.name} missing shebang line"
        )
        assert "bash" in first_line, (
            f"{bash_script.name} shebang does not reference bash"
        )

    def test_passes_syntax_check(self, bash_script):
        result = subprocess.run(
            ["bash", "-n", str(bash_script)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, (
            f"{bash_script.name} has syntax errors:\n{result.stderr}"
        )

    def test_is_not_empty(self, bash_script):
        content = bash_script.read_text(encoding="utf-8")
        non_blank = [l for l in content.splitlines() if l.strip()]
        assert len(non_blank) > 10, (
            f"{bash_script.name} seems too short to be functional"
        )


class TestMdmlinkStructure:
    @pytest.fixture(autouse=True)
    def _load(self, bash_script):
        if bash_script.name != "mdmlink":
            pytest.skip("not mdmlink")
        self.content = bash_script.read_text(encoding="utf-8")

    def test_defines_color_variables(self):
        for color in ("RED", "GRN", "BLU", "YEL", "PUR", "CYAN", "NC"):
            assert f"{color}=" in self.content, (
                f"mdmlink missing color variable {color}"
            )

    def test_has_select_menu(self):
        assert "select " in self.content, "mdmlink missing select menu"

    def test_has_case_statement(self):
        assert "case " in self.content, "mdmlink missing case statement"

    def test_has_esac(self):
        assert "esac" in self.content, "mdmlink missing esac (unterminated case)"

    def test_references_apple_mdm_hosts(self):
        assert "deviceenrollment.apple.com" in self.content
        assert "mdmenrollment.apple.com" in self.content
        assert "iprofiles.apple.com" in self.content

    def test_has_dscl_user_creation(self):
        assert "dscl" in self.content, "mdmlink missing dscl commands"

    def test_has_reboot_option(self):
        assert "reboot" in self.content
