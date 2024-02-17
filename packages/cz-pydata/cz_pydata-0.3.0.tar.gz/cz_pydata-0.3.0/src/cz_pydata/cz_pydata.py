from pathlib import Path

from commitizen.cz.base import BaseCommitizen
from commitizen.defaults import Questions

__all__ = ["PydataCz"]


class PydataCz(BaseCommitizen):
    """Commitizen for PyData-style commits.

    Use with `cz --name cz_pydata <command>`.
    """

    bump_pattern = r"^(API|BUG|DEP|ENH|FIX|NEW|REM|SEC)"
    bump_map = {
        "API": "MAJOR",
        "BUG": "PATCH",
        "DEP": "MINOR",
        "ENH": "MINOR",
        "FIX": "PATCH",
        "NEW": "MINOR",
        "REM": "MINOR",
        "SEC": "PATCH",
    }
    bump_map_major_version_zero = {
        "API": "MINOR",
        "BUG": "PATCH",
        "DEP": "MINOR",
        "ENH": "MINOR",
        "FIX": "PATCH",
        "NEW": "MINOR",
        "REM": "MINOR",
        "SEC": "PATCH",
    }

    commit_parser = r"^\[?(?P<change_type>API|BUG|DEP|ENH|FIX|NEW|REM|SEC)[\]:]?\s+(?P<message>.*)"
    changelog_pattern = r"^(API|BUG|DEP|ENH|FIX|NEW|REM|SEC)"
    change_type_map = {
        "API": "BREAKING CHANGES",
        "BUG": "Fixed",
        "DEP": "Deprecated",
        "ENH": "Changed",
        "FIX": "Fixed",
        "NEW": "Added",
        "REM": "Removed",
        "SEC": "Security",
    }
    change_type_order = [
        "BREAKING CHANGES",
        "Added",
        "Changed",
        "Deprecated",
        "Removed",
        "Fixed",
        "Security",
    ]

    def questions(self) -> Questions:
        """Questions regarding the commit message.

        Used by `cz commit`.
        """
        questions: Questions = [
            {
                "name": "acronym",
                "type": "list",
                "message": "Select the type of change",
                "choices": [
                    {"value": "API", "name": "API:   breaking change"},
                    {"value": "BENCH", "name": "BENCH: change to the benchmark suite"},
                    {"value": "BLD", "name": "BLD:   change to the build system"},
                    {"value": "BUG", "name": "BUG:   bug fix"},
                    {"value": "DEP", "name": "DEP:   deprecate a feature"},
                    {"value": "DEV", "name": "DEV:   development tool or utility"},
                    {"value": "DOC", "name": "DOC:   change to the documentation"},
                    {"value": "ENH", "name": "ENH:   improve a feature"},
                    {"value": "MAINT", "name": "MAINT: project maintenance"},
                    {"value": "NEW", "name": "NEW:   add a new feature"},
                    {"value": "REL", "name": "REL:   release a new version"},
                    {"value": "REM", "name": "REM:   remove a feature"},
                    {"value": "REV", "name": "REV:   revert an earlier commit"},
                    {"value": "SEC", "name": "SEC:   security-related change"},
                    {"value": "STY", "name": "STY:   style fix"},
                    {"value": "TST", "name": "TST:   change to the test suite"},
                    {"value": "TYP", "name": "TYP:   static typing"},
                    {"value": "WIP", "name": "WIP:   work-in-progress"},
                ],
            },
            {
                "name": "summary",
                "type": "input",
                "message": "Provide a summary of the change",
            },
            {
                "name": "description",
                "type": "input",
                "message": "Provide a description of the change (press [enter] to skip)",
            },
        ]

        return questions

    def message(self, answers: dict) -> str:
        """Generate the commit message based on the answers.

        Used by `cz commit`.
        """
        message = "{acronym}: {summary}".format(**answers)

        if description := answers.get("description", None):
            message = f"{message}\n\n{description}"

        return message

    def example(self) -> str:
        """Show an example of the commit message.

        Used by `cz example`.
        """
        return "BUG: Fix regression in some feature\n\nCloses: #3456"

    def schema(self) -> str:
        """Show the schema for the commit message.

        Used by `cz schema`.
        """
        return "<acronym>: <summary>\n<BLANK LINE>\n<description>"

    def schema_pattern(self) -> str:
        """Return the schema pattern for the commit message.

        Used by `cz check`.
        """
        return r"^\[?(API|BENCH|BLD|BUG|DEP|DEV|DOC|ENH|FIX|MAINT|MNT|NEW|REL|REM|REV|SEC|STY|TST|TYP|WIP)[\]:]?\s+(.*)"

    def info(self) -> str:
        """Show a detailed explanation of the commit rules.

        Used by `cz info`.
        """
        info_path = next(Path(__file__).parent.glob("*info.txt"))

        return info_path.read_text()
