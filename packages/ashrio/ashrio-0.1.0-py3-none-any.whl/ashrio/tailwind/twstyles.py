from pydantic import BaseModel
from typing import Union, Dict 

class Tailwind(BaseModel):
    tailwind_styles: str = ""


    def combine(self):
        return f""" class="{self.tailwind_styles}" """


    def get(self):
        # should be overridden with customizing the styles, but call the combine method
        pass 

