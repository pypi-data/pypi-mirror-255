from pydantic import BaseModel
from typing import Literal, List

class TextStyles(BaseModel):
    fontSize: int = 20
    variant: List[Literal["Bold", "Italics", "Underline"]] | None = None
    color: str = "#171717"  # hex code INCLUDING the hashtag
    fontFamily: Literal["Sans", "Serif"] = "Sans"

    def get(self) -> str:
        fontSize = f"font-size: {self.fontSize}px; "
        variant = ""
        color = f"color: {self.color}; "
        if self.fontFamily == "Sans":
            fontFamily = "font-family: sans-serif; "
        else:
            fontFamily = "font-family: serif; "

        if self.variant:
            for v in self.variant:
                if v == "Bold":
                    variant += "font-weight: bold; "
                elif v == "Italics":
                    variant += "font-style: italic; "  # Corrected to 'italic'
                elif v == "Underline":
                    variant += "text-decoration: underline; "

        return fontSize + color + fontFamily + variant

class TextDefaults(BaseModel):
    variant: Literal["Header", "Paragraph", "Subtitle"] # more to be implemented...

    def get(self) -> TextStyles:
        if self.variant == "Header":
            return TextStyles(fontSize=30, variant=["Bold"], fontFamily="Sans")
        elif self.variant == "Paragraph":
            return TextStyles(fontSize=20, fontFamily="Sans")
        elif self.variant == "Subtitle":
            return TextStyles(fontSize=25, fontFamily="Sans", variant=["Italics"], color="#333333")
        # more to be implemented... slowly but surely
