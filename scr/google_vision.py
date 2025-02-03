from google.cloud import vision
import io

def google_vision_extract(image_path):
    """
    Uses the Google Vision API to extract text from an image.
    
    Args:
        image_path (str): The file path of the image to be processed.
    
    Returns:
        str: Extracted text from the image or a message indicating no text was found.
    
    Raises:
        Exception: If an API error occurs.
    """
    client = vision.ImageAnnotatorClient()
    with io.open(image_path, 'rb') as image_file:
        content = image_file.read()
    image = vision.Image(content=content)
    response = client.text_detection(image=image)
    
    if response.error.message:
        raise Exception(f"API Error: {response.error.message}")
    
    texts = response.text_annotations
    return texts[0].description if texts else "No text found."
