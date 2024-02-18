from pydantic import BaseModel
from typing import List, Literal, Optional, Dict
from ..tailwind import Tailwind

class ButtonStyles(BaseModel):
    size: Literal["Small", "Medium", "Large"] = "Medium"
    backgroundColor: Literal["Primary", "Secondary", "Success"] | str = "Primary"
    textColor: str = "#ffffff"  # Default to white text
    borderStyle: Literal["None", "Solid", "Dashed", "Dotted"] = "Solid"
    borderRadius: Literal["Rounded", "Rounded-XL", "Rounded-SM", "Rounded-MD", "Rounded-LG"] | int = "Rounded"
    fontWeight: Literal["Normal", "Bold"] = "Normal"
    fontSize: Optional[int] = None  # Allow users to optionally set font size

    def get(self) -> str:
        size_map = {
            "Small": "padding: 5px 10px; font-size: 12px;",
            "Medium": "padding: 10px 20px; font-size: 14px;",
            "Large": "padding: 15px 30px; font-size: 16px;",
        }

        background_color_map = {
            "Primary": "#007bff",
            "Secondary": "#6c757d",
            "Success": "#28a745",
        }

        border_radius_map = {
            "Rounded": "border-radius: 5px;",
            "Rounded-SM": "border-radius: 2px;",
            "Rounded-MD": "border-radius: 8px;",
            "Rounded-LG": "border-radius: 12px;",
            "Rounded-XL": "border-radius: 20px;",
        }

        background_color = background_color_map.get(self.backgroundColor, self.backgroundColor)
        border_radius = border_radius_map.get(self.borderRadius, f"border-radius: {self.borderRadius}px;") if isinstance(self.borderRadius, str) else f"border-radius: {self.borderRadius}px;"

        styles = f"""
            background-color: {background_color};
            color: {self.textColor};
            border: 2px {self.borderStyle.lower()} #dee2e6;
            {border_radius}
            font-weight: {self.fontWeight.lower()};
            {size_map[self.size]}
            cursor: pointer;
        """

        if self.fontSize:
            styles += f"font-size: {self.fontSize}px; "

        return " ".join(styles.split())  # Clean up whitespace for a tidier output


# Better for non-dynamic things...
class ButtonStylesTW(Tailwind):
    rounded: Literal["Sm", "Md", "Lg", "Xl"] = "Md"
    buttonColor: Dict[Literal["Gray", "Red", "Green", "Blue"], Literal[100, 300, 500, 900]] | str = {"Gray": 500}
    font: Literal["Sans", "Serif"] = "Sans"
    size: Literal["Sm", "Md", "Lg", "Xl"] = "Md"
    fontColor: Literal["Offwhite", "Offblack"] = "Offblack"
    #shape: Literal["Rectangle", "Square"] = "Rectangle"

    def get(self):
        roundedMapping = {
            "Sm": "rounded-sm",
            "Md": "rounded",
            "Lg": "rounded-lg",
            "Xl": "rounded-xl"
        }
        buttonColorNameMapping = {
            "Gray": "bg-gray-{number}",
            "Red": "bg-rose-{number}",
            "Green": "bg-green-{number}",
            "Blue": "bg-blue-{number}"
        }

        fontMapping = {
            "Sans": "font-sans",
            "Serif": "font-serif"
        }

        sizeMapping = {
            "Sm": "w-24 h-10",
            "Md": "w-36 h-16",
            "Lg": "w-48 h-28",
            "Xl": "w-60 h-32"
        }

        fontColor = "text-gray-200" if self.fontColor == "Offwhite" else "text-gray-900"
        tailwind = [fontColor]

        tailwind.append(roundedMapping.get(self.rounded, ""))
        tailwind.append(buttonColorNameMapping.get(list(self.buttonColor.keys())[0]).format(number=list(self.buttonColor.values())[0]))
        tailwind.append(fontMapping.get(self.font))
        tailwind.append(sizeMapping.get(self.size))

        output = " ".join(word for word in tailwind)
        self.tailwind_styles = output 
        print(self.combine())

        return self.combine()


