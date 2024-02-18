from text.text import Text
from text.styles import TextStyles

text_styles = TextStyles(variant=["Bold", "Underline"], fontSize=25, fontFamily="Sans")
# This will create a new HTML file with the basic structure and add the first content
text_example = Text(content="Hello, world!", styles=text_styles)
text_example.write_to_file(method="w")

# This will append new content to the existing HTML file
text_2 = Text(content="Another example text.")
text_2.write_to_file(method="a")
