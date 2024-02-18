from pydantic import BaseModel
from typing import Any, Dict, Optional

class EventHandler(BaseModel):
    event: str
    action: str  # Changed from Callable to str to directly provide JavaScript code
    params: Dict[str, Any] = {}

    def get_alpine_directive(self) -> str:
        # Directly use action as the JavaScript code for Alpine.js
        return f"x-on:{self.event}=\"{self.action}\""
