from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path
import os
import pandoc
import sys
import traceback


def remove_empty_tags(soup):
    # Remove all empty <li> and <td> elements inside the <body> tag
    for empty_tag in soup.body.find_all(["a", "li", "p", "td", "ul"]):
        if not empty_tag.text.strip():
            empty_tag.decompose()

    return soup


def remove_non_printable(soup):
    for hidden in soup.body.select(
        ", ".join(
            [
                ".material-icons-outlined",
                ".btn",
                ".articleMenu",
                "section.levelMenu",
                "div.col-md-2.md-body-dashVertical",
                "#ModalScimago",
                "#ModalDownloads",
                "#ModalVersionsTranslations",
                "#metric_modal_id",
                "#ModalHowcite",
            ]
        )
    ):
        hidden.decompose()

    for broken_link in soup.body.find_all("a", href=True):
        href = broken_link["href"]
        if href.startswith("http") or href.startswith("//"):
            print(f"Keeping link: {broken_link['href']}")
            continue
        broken_link.decompose()

    return soup


def fix_headings(soup):
    h1_title = soup.body.find("h1", class_="article-title")
    if h1_title:
        h1_title.decompose()
        for h in range(2, 7):
            for heading in soup.body.find_all(f"h{h}"):
                heading.name = f"h{h-1}"

    return soup


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
        fyle = read_file(input_file)
        soup = BeautifulSoup(fyle, "html.parser")
        soup = remove_non_printable(soup)
        soup = fix_headings(soup)
        soup = remove_empty_tags(soup)

        meta_title = None
        if soup.head:
            meta_title = soup.head.find("meta", property="og:title")
            print(f"Meta title found: {meta_title}")

            if meta_title and meta_title.get("content"):
                title_text = meta_title["content"]
                if soup.title:
                    soup.title.string = title_text
                else:
                    new_title_tag = soup.new_tag("title")
                    new_title_tag.string = title_text
                    soup.head.append(new_title_tag)

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
            for css_file in css_files:
                with open(css_file, "r", encoding="utf-8") as f:
                    css += f.read() + "\n"
            css += "sup { vertical-align: super !important; }"
            # print(f"Detected CSS files: {css_files}")

            soup.head.append(soup.new_tag("style", type="text/css"))
            soup.head.style.string = css
        else:
            print(f"CSS folder '{css_folder}' does not exist.")

        # Remove all <link> tags in the <head> that point to CSS files
        for link_tag in soup.head.find_all("link", rel="stylesheet"):
            link_tag.decompose()

        # Write the processed HTML back to the original file
        # with open(input_file, "w", encoding="utf-8") as output_file:
        #     output_file.write(str(soup))

        # Convert the processed HTML to ODT using Pandoc
        try:
            reference_doc = Path(__file__).parent / "tablet.html.odt"
            lang_attr = soup.html.get("lang", "pt-BR")
            pandoc_html = pandoc.read(source=str(soup), format="html")
            output_odt = str(pathable.with_suffix(".odt"))
            # output_pdf = str(pathable.with_suffix(".pdf"))
            pandoc.write(
                pandoc_html,
                format="odt",
                file=output_odt,
                options=[
                    f"--resource-path={css_folder}",
                    f"--reference-doc={reference_doc}",
                    "-V",
                    f"lang={lang_attr}",
                ],
            )
            # pandoc_odt = pandoc.read(file=output_odt, format="odt")
            # pandoc.write(pandoc_odt, format="pdf", file=output_pdf)

            print(f"Converted HTML to ODT: {output_odt}")
        except Exception as e:
            print(f"Failed to convert HTML to ODT: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_html_file>")
    else:
        process_html_file(sys.argv[1])
