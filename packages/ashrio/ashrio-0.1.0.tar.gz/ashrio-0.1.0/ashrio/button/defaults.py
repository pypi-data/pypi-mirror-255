from pydantic import BaseModel

class ButtonAlert(BaseModel):
    alert_text: str

    def get(self):
        return f"alert('{self.alert_text}')"

class ButtonLink(BaseModel):
    url: str

    def get(self):
        # Correct the quoting for the JavaScript function
        return f"window.location.href='{self.url}';", "Redirect"

class ButtonModal(BaseModel):
    id: str

    def get(self):
        return f"document.getElementById('{self.id}').style.display='block';"
