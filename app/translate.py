import requests
from flask_babel import _
from app import app

api_key = app.config["TRANSLATE_KEY"]


def translate(text, source_lan: str, dest_lang: str):
    url = "https://translate.brave.com/translate_a/t?anno=3&client=te_lib&format=html&v=1.0&key={api_key}&logld=vTE_20220615&sl={source_lang}&tl={dest_lang}&tc=1&sr=1&mode=1".format(
        api_key=api_key, source_lang=source_lan, dest_lang=dest_lang
    )
    payload = {"q": text}

    response = requests.request("POST", url, data=payload)
    if response.status_code != 200:
        return _("Error: the translation service failed.")
    return response.json()[0]