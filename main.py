import sys
from bs4 import BeautifulSoup
import os
from datetime import datetime

def process_html_file(input_file):
  try:
    # Open and read the HTML file
    with open(input_file, 'r', encoding='utf-8') as file:
      soup = BeautifulSoup(file, 'html.parser')

      # Create a backup of the original file with a timestamp
      timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
      base, ext = os.path.splitext(input_file)
      backup_file = f"{base}_{timestamp}{ext}"
      with open(backup_file, 'w', encoding='utf-8') as backup:
        backup.write(str(soup))

      # Remove all empty <li> and <td> elements inside the <body> tag
      for empty_tag in soup.body.find_all(['a', 'li', 'p', 'td']):
        if not empty_tag.text.strip():
          empty_tag.decompose()

    # Remove all <script> tags
    for script in soup.find_all(['form', 'script']):
      script.decompose()

      # Remove all <a> tags with href starting with "javascript:"
      for a_tag in soup.find_all('a', href=True):
        if a_tag['href'].startswith('javascript:'):
          a_tag.decompose()

    # Save the cleaned HTML back to the file
    with open(input_file, 'w', encoding='utf-8') as file:
      file.write(str(soup))

    print(f"File '{input_file}' processed successfully.")
  except Exception as e:
    print(f"An error occurred: {e}")

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python main.py <path_to_html_file>")
  else:
    process_html_file(sys.argv[1])