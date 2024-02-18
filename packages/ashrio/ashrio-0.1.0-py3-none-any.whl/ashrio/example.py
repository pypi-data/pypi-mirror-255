from text import Text
from text import TextStyles, TextDefaults
from button import Button
from grid import Grid
from button import ButtonStyles,ButtonModal
from modal import Modal
from card import Card, CardAction

textstyles = TextStyles(variant=["Bold", "Underline"], fontSize=15, fontFamily="Sans")
header = TextDefaults(variant="Header").get()
buttonstyles = ButtonStyles(backgroundColor="Primary", size="Medium", borderRadius="Rounded-LG").get()


my_modal_text = Text(content="Hello, Modal!", styles=textstyles, filepath="./output.html"
)
my_modal = Modal(
    id="myModal",
    title="My Modal Title",
    title_style=header,
    content=my_modal_text,
    content_style=TextDefaults(variant="Paragraph").get()
)

# Create a grid
my_grid = Grid(rows=4, cols=4, gap=15)

# Create text and button components
my_text = Text(content="Hello, Grid!", styles=header, filepath="./output.html")
my_button = Button(text="Click Me", onclick="alert('Button clicked!')", filepath="./output.html", styles=buttonstyles)

button_2 = Button(text="Open", onclick=ButtonModal(id=my_modal.id).get(), filepath="./output.html", styles=buttonstyles)

# Define actions for the card
card_actions = [
    CardAction(label="Click Me", onclick="alert('Hello World')"),
    CardAction(label="Visit", onclick="window.location.href='https://example.com'")
]

# Create a card instance
my_card = Card(
    title="Card Title",
    title_style=header,
    content="This is the content of the card. It can be simple text or structured HTML.",
    actions=card_actions
)

my_card.write_to_file(method='w')


# Add components to the grid

my_grid.add_item(my_modal, row_start=1, col_start=1, row_end=4, col_end=4)
my_grid.add_item(my_card, row_start=3, col_start=5, row_end=4, col_end=4)
my_grid.add_item(button_2, row_start=1, col_start=1, row_end=2, col_end=2)



# Write the grid to file
my_grid.write_to_file(method='w')
