from pydantic import BaseModel
from typing import Union, Any
from ..utils import write_to_file
from ..text import TextStyles

class Modal(BaseModel):
    id: str  # Unique identifier for the modal
    title: str  # Title displayed on the modal
    title_style: Union[TextStyles, None] = None  # Optional TextStyles for the title
    content: Union[str, Any]  # Content could be a string or any class instance
    content_style: Union[TextStyles, None] = None  # Optional TextStyles for the content
    filepath: str = './output.html'

    def write_to_file(self, method="a"):
        modal_html = self.get_html()
        write_to_file(modal_html, self.filepath, method)

    def get_html(self, style_extra=""):
        title_style = self.title_style.get() if self.title_style else ""

        # Render content based on its type
        if hasattr(self.content, 'get_html'):
            content_html = self.content.get_html()  # Call the method if it's a class instance
        else:
            content_style = self.content_style.get() if self.content_style else ""
            content_html = f'<p style="{content_style}">{self.content}</p>'  # Treat as plain text otherwise

        return f"""
<div id="{self.id}" style="display:none; position: fixed; z-index: 1; left: 0; top: 0; width: 100%; height: 100%; overflow: auto; background-color: rgba(0,0,0,0.4); padding-top: 60px; border-radius: 15; {style_extra}">
    <div style="background-color: #fefefe; margin: 5% auto; padding: 20px; border: 1px solid #888; width: 80%; border-radius: 15px;">
        <div style="display: flex; justify-content: space-between; align-items: center; border-radius: 15;">
            <h2 style="{title_style}">{self.title}</h2>
            <button onclick="document.getElementById('{self.id}').style.display='none'" style="font-size: 25px; border: none; cursor: pointer;">&times;</button>
        </div>
        {content_html}
    </div>
</div>
<script>
function showModal(id) {{
    document.getElementById(id).style.display = 'block';
}}
</script>
        """
