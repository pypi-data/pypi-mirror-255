from pydantic import BaseModel
from typing import Optional, Dict, Any
from ashrio import write_to_file, TextStyles
from .core import EventHandler
import json  # Import the json module

class StatefulText(BaseModel):
    initial_state: Dict[str, Any]
    styles: str | TextStyles = ""
    filepath: str = "./output.html"
    event_handlers: Optional[Dict[str, EventHandler]] = None

    def write_to_file(self, method="a"):
        # Serialize initial_state to a JSON string for Alpine.js x-data
        alpine_data = f"x-data='{{\"text\": \"{self.initial_state['text']}\"}}'"
        # Generate all event directives from event_handlers
        event_directives = " ".join([handler.get_alpine_directive() for handler in self.event_handlers.values()]) if self.event_handlers else ""
        # Include x-text to bind the div's content to the Alpine.js data model's text property
        html_content = f'<div {alpine_data} {event_directives} style="{self.styles if isinstance(self.styles, str) else self.styles.get()}" x-text="text"></div>'
        write_to_file(html_content, self.filepath, method)

    def get_html(self, style_extra=""):
        alpine_data = f"x-data='{{\"text\": \"{self.initial_state['text']}\"}}'"
        event_directives = " ".join([handler.get_alpine_directive() for handler in self.event_handlers.values()]) if self.event_handlers else ""
        html_content = f'<div {alpine_data} {event_directives} style="{self.styles if isinstance(self.styles, str) else self.styles.get()}; {style_extra}" x-text="text"></div>'
        return html_content
