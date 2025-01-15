from google.cloud import vision
import io

def google_vision_extract(image_path):
    """Usa a API do Google Vision para extrair texto de uma imagem."""
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    if response.error.message:
        raise Exception(f"Erro da API: {response.error.message}")
    texts = response.text_annotations
    return texts[0].description if texts else "Nenhum texto encontrado."
