"""Format README python snippets with the results of print statements in comment."""

import io
import sys
from pathlib import Path

# Configuration
INPUT_DIR = Path("dev/readme_snippets/raw/")
OUTPUT_DIR = Path("dev/readme_snippets/formatted/")
GLOB_PATTERN = "*.py"


def process_print_output(output: str) -> str:
    """Format the print output."""
    return f"  # Output: {output}" if output else ""


def execute_and_capture_prints(code: str) -> list[str]:
    """Execute the code and capture all print outputs."""
    captured_output = io.StringIO()
    sys.stdout = captured_output

    try:
        exec(code)
    except Exception as e:
        captured_output.write(f"Error: {e}")

    sys.stdout = sys.__stdout__
    return captured_output.getvalue().strip().splitlines()


def process_file(input_file_path: Path, output_file_path: Path) -> None:
    """Process a Python file and write formatted content with print outputs."""
    with input_file_path.open() as f:
        lines = f.readlines()

    print_outputs = execute_and_capture_prints("".join(lines))

    formatted_lines = []
    print_index = 0

    # Go through the lines and add the captured print output as comments
    for line in lines:
        formatted_lines.append(line)  # Always append the original line
        if "print(" in line:
            formatted_output = process_print_output(print_outputs[print_index])
            formatted_lines[-1] = f"{line.strip()}{formatted_output}\n"  # Add comment with output
            print_index += 1

    with output_file_path.open("w") as f:
        f.writelines(formatted_lines)


def process_directory(input_dir: Path, output_dir: Path) -> None:
    """Iterate over all Python files in the input directory and process each."""
    output_dir.mkdir(parents=True, exist_ok=True)

    for input_file_path in input_dir.glob(GLOB_PATTERN):
        output_file_path = output_dir / input_file_path.name
        process_file(input_file_path, output_file_path)


if __name__ == "__main__":
    process_directory(INPUT_DIR, OUTPUT_DIR)