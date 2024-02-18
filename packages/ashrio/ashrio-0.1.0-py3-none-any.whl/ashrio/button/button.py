from pydantic import BaseModel
from ..utils.core import write_to_file
from .styles import ButtonStyles
from .styles import ButtonStylesTW

class Button(BaseModel):
    text: str
    onclick: str  # JavaScript function as a string
    filepath: str = './output.html'
    styles: ButtonStyles | str | ButtonStylesTW = ButtonStyles(backgroundColor="Primary", size="Medium").get()
    value: str = ""

    def write_to_file(self, method="a"):
        # Improved handling for HTML attributes with proper escaping
        if isinstance(self.styles, ButtonStylesTW):
            classes = self.styles.get()
        else:
            classes = ""
        
        value_attr = f"value='{self.value}'" if self.value else ""
        button_html = f'<button {classes}   {value_attr} style="{self.styles if isinstance(self.styles, str) else self.styles.get() if isinstance(self.styles, ButtonStyles) else ""}" onclick=\"{self.onclick}\">{self.text}</button>\n'
        write_to_file(button_html, self.filepath, method)

    def get_html(self, style_extra=""):
        value_attr = f"value='{self.value}'" if self.value else ""
        button_html = f'<button  {classes} {value_attr} style="{self.styles if isinstance(self.styles, str) else self.styles.get()}; {style_extra}" onclick="{self.onclick}">{self.text}</button>'
        return button_html
