from pydantic import BaseModel
from typing import Literal, List, ClassVar
from ..utils.core import write_to_file
from .styles import TextStyles

class Text(BaseModel):
    content: str
    styles: str | TextStyles = ""  # CSS styles
    filepath: str = "./output.html"

    def write_to_file(self, method="a"):
        # Apply the style attribute directly to the div
        html_content = f'<div style="{self.styles if isinstance(self.styles, str) else self.styles.get()}">{self.content}</div>'
        write_to_file(html_content, self.filepath, method)

    def get_html(self, style_extra=""):
        html_content = f'<div style="{self.styles if isinstance(self.styles, str) else self.styles.get()}; {style_extra}">{self.content}</div>'
        return html_content
