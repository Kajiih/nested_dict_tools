"""Parse and input code snippets in a markdown file. Currently only works for python snippets."""

import re
from pathlib import Path
from re import Match

# Define directories for snippets and the README file
README_PATH = Path("README.md")  # Path to your README file
SNIPPET_DIR = Path("dev/readme_snippets/formatted/")  # Directory containing the snippet files


def load_snippet(snippet_name: str) -> str:
    """Load the content of the snippet file given the snippet's name."""
    snippet_path = SNIPPET_DIR / f"{snippet_name}.py"

    with snippet_path.open() as file:
        return file.read()


def replace_snippets_in_readme(readme_path: Path) -> None:
    """Read the README file, replace the snippet placeholders, and save the modified README."""
    with readme_path.open() as file:
        readme_content = file.read()

    # Regular expression to match the snippet placeholders
    snippet_pattern = r"<!-- snippet: (\w+) -->\s*```python\n(.*?)```"

    def replace_snippet(match: Match[str]) -> str:
        snippet_name = match.group(1)
        snippet_code = load_snippet(snippet_name)

        snippet_code = snippet_code.rstrip("\n")  # Strip trailing newline

        return f"<!-- snippet: {snippet_name} -->\n```python\n{snippet_code}\n```"

    # Replace all occurrences of the snippet placeholders in the README
    updated_readme_content = re.sub(
        snippet_pattern, replace_snippet, readme_content, flags=re.DOTALL
    )

    with readme_path.open("w") as file:
        file.write(updated_readme_content)


if __name__ == "__main__":
    replace_snippets_in_readme(README_PATH)
