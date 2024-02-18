from pydantic import BaseModel, BaseConfig
from typing import Literal, List, ClassVar, Dict


def write_to_file(content, filepath, method='a'):
    if method == 'w':
        # Creating a new HTML document with the content
        full_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Generated Page</title>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body>
{content}
</body>
</html>"""
    else:
        # Appending content to an existing HTML document
        try:
            with open(filepath, 'r+') as file:
                file_content = file.read()
                insert_position = file_content.rfind('</body>')
                if insert_position != -1:
                    # Insert the new content just before the </body> tag
                    file_content = f"{file_content[:insert_position]}{content}\n{file_content[insert_position:]}"
                    file.seek(0)  # Go back to the start of the file
                    file.write(file_content)  # Rewrite with new content
                    file.truncate()  # Remove any remaining original content after the new end
                else:
                    raise ValueError("No </body> tag found in the existing HTML document.")
        except FileNotFoundError:
            print("File not found. Creating a new file.")
            method = 'w'  # Switch to write mode to create the file if it doesn't exist
            return write_to_file(content, filepath, method)

    # If creating a new file, this part is executed
    if method == 'w':
        with open(filepath, 'w') as file:
            file.write(full_content)

