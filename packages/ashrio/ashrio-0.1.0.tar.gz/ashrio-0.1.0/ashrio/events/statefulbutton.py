from pydantic import BaseModel
from typing import Optional, Dict, Any
from ashrio import write_to_file, ButtonStyles  # Adjust the import path as necessary
from .core import EventHandler  # Adjust the import path as necessary
import json

class StatefulButton(BaseModel):
    initial_state: Dict[str, Any] # can include props, styles, and tailwind
    filepath: str = "./output.html"
    event_handlers: Optional[Dict[str, EventHandler]] = None

    def write_to_file(self, method="a"):
        # Serialize initial_state to a JSON string for Alpine.js x-data
        alpine_data = f"x-data='{json.dumps(self.initial_state)}'"
        # Generate all event directives from event_handlers
        event_directives = " ".join([handler.get_alpine_directive() for handler in self.event_handlers.values()]) if self.event_handlers else ""
        # Directly apply styles without dynamic binding
        button_html = f'<button {alpine_data} {event_directives} style="{self.initial_state.get("styles", "")}" x-text="text"></button>'
        write_to_file(button_html, self.filepath, method)

    def get_html(self):
        # Serialize initial_state to a JSON string for Alpine.js x-data
        alpine_data = f"x-data='{json.dumps(self.initial_state)}'"
        # Generate all event directives from event_handlers
        event_directives = " ".join([handler.get_alpine_directive() for handler in self.event_handlers.values()]) if self.event_handlers else ""
        # Directly apply styles without dynamic binding
        button_html = f'<button {alpine_data} {event_directives} class="{self.initial_state.get("tailwind", "")}" style="{self.initial_state.get("styles", "")}" x-text="text"></button>'
        return button_html