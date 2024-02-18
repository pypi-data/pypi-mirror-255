from pydantic import BaseModel
from typing import List, Optional, Union, Any
from ..utils import write_to_file
from ..text.styles import TextStyles

class CardAction(BaseModel):
    label: str
    onclick: str  # JavaScript function or URL for action

class Card(BaseModel):
    title: str
    title_style: Optional[TextStyles] = None  # Optional TextStyles for the title
    content: Union[str, Any]  # Allows for string content or any object with a get_html method
    actions: Optional[List[CardAction]] = None
    filepath: str = './output.html'

    def write_to_file(self, method="a"):
        card_html = self.get_html()
        write_to_file(card_html, self.filepath, method)

    def get_html(self, style_extra=""):
        # Apply title styles if provided
        title_style = self.title_style.get() if self.title_style else "font-size: 24px; font-weight: bold;"  # Default style for title

        # Create action buttons if any
        actions_html = ""
        if self.actions:
            actions_html = "".join([f'<button onclick="{action.onclick}">{action.label}</button>' for action in self.actions])

        # Check for content object with get_html method
        if hasattr(self.content, 'get_html'):
            content_html = self.content.get_html()
        else:
            content_html = self.content

        # Embedding enhanced CSS for the card
        styles = """
<style>
.card {
    box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);
    transition: 0.3s;
    border-radius: 10px; /* Rounded corners */
    background-color: #fff; /* White background */
    margin: 10px 0; /* Margin for spacing */
    width: auto; /* Adjust width as needed */
}
.card-container {
    padding: 16px;
}
.card-title {
    margin-bottom: 15px;
}
.card button {
    cursor: pointer;
    padding: 10px;
    border: none;
    border-radius: 5px;
    margin-right: 10px;
    background-color: #007bff;
    color: white;
}
.card button:hover {
    opacity: 0.8;
}
</style>
        """

        return f"""
<div class="card rounded-xl border bg-card text-card-foreground shadow" style="{style_extra}">
    <div class="card-container flex flex-col space-y-1.5 p-6">
        <h4 class="card-title font-semibold leading-none tracking-tight " style="{title_style}">{self.title}</h4>
        <p>{content_html}</p>
        <div>{actions_html}</div>
    </div>
</div>
        """
