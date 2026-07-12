import os
import json
from logging_config import logger
from markdown_it import MarkdownIt

TAG = 'data_retrieval_handbook'

def parse_markdown_to_header_content(file_path):
    """
    Parses a Markdown file and extracts headers and content as a list of dictionaries.
    Each dictionary contains a header and its associated content.
    Filters out:
        - Empty headers or content.
        - Headers starting with a < tag element.
    """
    with open(file_path, 'r') as f:
        md_content = f.read()
    logger.info(f"{TAG}:Reading data from '{file_path}' file")
    
    # Initialize Markdown parser
    md = MarkdownIt()
    tokens = md.parse(md_content)

    # Parse headers and content
    data = []
    current_header = None
    current_content = []

    for token in tokens:
        if token.type == "heading_open":
            # Save the previous header and its content before starting a new header
            if current_header:
                # Only add if both header and content are non-empty and header doesn't start with a < tag
                if current_header.strip() and "".join(current_content).strip() and not current_header.strip().startswith("<"):
                    data.append({
                        "header": current_header.strip(),
                        "content": " ".join(current_content).strip()
                    })
            current_header = None
            current_content = []
        elif token.type == "inline" and current_header is None:
            current_header = token.content
        elif token.type == "inline" and current_header:
            # Collect inline text content for the current header
            current_content.append(token.content)

    # Add the last header and content if valid
    if current_header and "".join(current_content).strip() and not current_header.strip().startswith("<"):
        data.append({
            "header": current_header.strip(),
            "content": " ".join(current_content).strip()
        })

    return data

def convert_markdown_folder_to_json(input_folder, output_file):
    """
    Converts all Markdown files in a folder (including nested folders) to a JSON file in header-content format.
    Filters out:
        - Empty headers or content.
        - Headers starting with a < tag element.
    """
    all_data = []
    for root, _, files in os.walk(input_folder):
        for filename in files:
            if filename.endswith(".md"):
                file_path = os.path.join(root, filename)
                parsed_data = parse_markdown_to_header_content(file_path)
                all_data.extend(parsed_data)

    # Ensure the output directory exists
    os.makedirs('data', exist_ok=True)

    # Write the combined data to a JSON file
    with open(f'data/{output_file}', 'w') as f:
        json.dump(all_data, f, indent=4)

    print(f"Data has been written to data/{output_file}")

# Define paths
input_folder = "./handbook"  # Replace with your folder containing .md files
output_file = "handbook_from_md.json"  # Replace with the desired output file name

# Convert Markdown files to JSON
convert_markdown_folder_to_json(input_folder, output_file)
