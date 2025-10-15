from bs4 import BeautifulSoup
import css_inline
from datetime import datetime
from pathlib import Path
import os
import sys
import traceback


def read_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()


def backup_file(file_path):
    fyle = read_file(file_path)
    # Create a backup of the original file with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base, ext = os.path.splitext(file_path)
    backup_file = f"{base}.{timestamp}{ext}"
    with open(backup_file, "w", encoding="utf-8") as backup:
        backup.write(fyle)

    return fyle


def process_html_file(input_file):
    try:
        fyle = backup_file(input_file)
        soup = BeautifulSoup(fyle, "html.parser")

        # Adiciona "https:" a links que começam com //
        for link_tag in soup.head.find_all("link", rel="stylesheet"):
            url = link_tag.get("href")
            if url is not None and url.startswith("//"):
                link_tag["href"] = f"https:{url}"

        pathable = Path(input_file)
        # Extract the stem of the file (filename without extension)
        file_stem = pathable.stem

        # Construct the folder name based on the stem
        css_folder = pathable.parent / f"{file_stem}_arquivos"
        print(f"Looking for CSS files in folder: {css_folder}")

        css = ""

        # Check if the folder exists
        if os.path.isdir(css_folder):
            # Detect all CSS files in the folder
            css_files = [
                os.path.join(css_folder, f) for f in os.listdir(css_folder) if f.endswith(".css")
            ]
            css = ""
            for css_file in css_files:
                with open(css_file, "r", encoding="utf-8") as f:
                    css += f.read() + "\n"
            # print(f"Detected CSS files: {css_files}")

            soup.head.append(soup.new_tag("style", type="text/css"))
            soup.head.style.string = css
        else:
            print(f"CSS folder '{css_folder}' does not exist.")

        # Remove all <link> tags in the <head> that point to CSS files
        for link_tag in soup.head.find_all("link", rel="stylesheet"):
            link_tag.decompose()

        parsed_html = str(soup)
        # print(parsed_html)

        # Use css_inline to inline CSS styles
        inlined_html = css_inline.inline(parsed_html)
        # print(css)

        # Write the processed HTML back to the original file
        with open(input_file, "w", encoding="utf-8") as output_file:
            output_file.write(inlined_html)
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_html_file>")
    else:
        process_html_file(sys.argv[1])
