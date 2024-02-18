from pydantic import BaseModel
from typing import List, Dict, Union, Literal
from ..utils.core import write_to_file
from ..text.text import Text
from ..button.button import Button

class Grid(BaseModel):
    rows: int
    cols: int
    gap: int = 10  # Default gap between grid items
    items: List[Dict[str, Union[str, BaseModel]]] = []
    filepath: str = "./output.html"

    def add_item(self, item: BaseModel, row_start: int, col_start: int, row_end: int = None, col_end: int = None):
        self.items.append({
            "item": item,
            "position": (row_start, col_start, row_end, col_end)
        })

    def render(self):
        grid_style = f"display: grid; grid-template-rows: repeat({self.rows}, 1fr); grid-template-columns: repeat({self.cols}, 1fr); gap: {self.gap}px;"
        grid_items_html = ""
        for item in self.items:
            item_obj, position = item["item"], item["position"]
            item_style = f"grid-row: {position[0]} / {position[2] if position[2] else 'span 1'}; grid-column: {position[1]} / {position[3] if position[3] else 'span 1'};"
            item_html = item_obj.get_html(style_extra=item_style)
            grid_items_html += item_html

        return f'<div style="{grid_style}">{grid_items_html}</div>'

    def write_to_file(self, method="w"):
        grid_html = self.render()
        write_to_file(grid_html, self.filepath, method)
