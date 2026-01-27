from urllib.parse import quote

def whatsapp_url(owner_number: str, message: str):
    msg = quote(message)
    return f"https://wa.me/{owner_number}?text={msg}"
