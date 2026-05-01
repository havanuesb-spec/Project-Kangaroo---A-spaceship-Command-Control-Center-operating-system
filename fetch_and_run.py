import requests
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
import subprocess
import tempfile
import os


URL = "c:\\Multiverse\\jscjr_multiverse.pys/App%20Concept%20Breakdown%20mverse-py%20codes.html"  # <-- change this


def get_python_code(url):
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Try to find code blocks
    code_block = soup.find("pre") or soup.find("code")

    if not code_block:
        raise Exception("No code block found on page")

    return code_block.get_text()


def run_code(code):

    # Create temp file
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".py",
        delete=False
    ) as f:

        f.write(code)
        filename = f.name

    print("Saved to:", filename)

    # Run it
    subprocess.run(["python", filename])

    # Optional cleanup
    os.remove(filename)


def main():
    code = get_python_code(URL)
    run_code(code)


if __name__ == "__main__":
    main()