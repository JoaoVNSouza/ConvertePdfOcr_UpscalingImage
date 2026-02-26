from google import genai
from google.genai import types
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.environ.get("API_KEY")
PROMPT = os.environ.get("PROMPT")
PATH_IMAGE_GENERATED = os.environ.get("PATH_IMAGE_GENERATED")


def gerar_imagem(path_img) -> bool:
    client = genai.Client(api_key=os.environ.get("API_KEY"))

    imagem = Image.open(path_img)

    response = client.models.generate_content(
        model="gemini-3-pro-image-preview",
        contents=[PROMPT, imagem],
    )

    for part in response.parts:
        if part.text is not None:
            print(part.text)
        elif part.inline_data is not None:
            image = part.as_image()
            image.save(PATH_IMAGE_GENERATED)
            return True

    return False
