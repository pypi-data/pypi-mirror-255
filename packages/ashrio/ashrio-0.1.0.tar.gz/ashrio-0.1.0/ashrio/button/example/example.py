from button.button import Button, ButtonAlert, ButtonLink

onclick, value = ButtonLink(url="https://google.com").get()


button_example = Button(text="Hi", onclick=onclick, value=value)


button_example.write_to_file(method="w")
