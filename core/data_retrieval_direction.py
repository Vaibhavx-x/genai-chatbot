from bs4 import BeautifulSoup
import json
import requests

TAG='data_retrieval_direction'
# Load HTML content (you can load this from a file or directly from the HTML string)
url='https://about.gitlab.com/direction/'
html_content = requests.get(url) # replace with your HTML content
soup = BeautifulSoup(html_content.text, 'html.parser')

# Find all headers and their following content
data = []
current_section = {"header": None, "content": ""}

# Define header tags and paragraph tags
header_tags = ["h1", "h2", "h3", "h4", "h5", "h6"]
content_tags = ["p", "li"]

for tag in soup.find_all(header_tags + content_tags):
    if tag.name in header_tags:
        # If there's a current section, add it to the data list before starting a new one
        if current_section["header"]:
            data.append(current_section)
        # Start a new section with the current header
        current_section = {"header": tag.get_text(strip=True), "content": ""}
    elif tag.name in content_tags and current_section["header"]:
        # Append content to the current section
        current_section["content"] += " " + tag.get_text(strip=True)

# Add the last section if it exists
if current_section["header"]:
    data.append(current_section)

# Convert to JSON
json_data = json.dumps(data, ensure_ascii=False, indent=2)

# Save to file
with open("data/direction_from_web.json", "w", encoding="utf-8") as f:
    f.write(json_data)

print(json_data)
