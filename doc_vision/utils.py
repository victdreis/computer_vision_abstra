from google.cloud import language_v1

def google_nlp_analyze_entities(text_content):
    """Uses Google Natural Language API to analyze entities in text."""
    client = language_v1.LanguageServiceClient()

    # Create a document for the text content
    document = language_v1.Document(
        content=text_content, type_=language_v1.Document.Type.PLAIN_TEXT
    )

    # Perform entity analysis
    response = client.analyze_entities(document=document)

    # Organize entities into a dictionary
    entities = {}
    for entity in response.entities:
        entities[entity.name] = language_v1.Entity.Type(entity.type_).name

    return entities

def list_visible_information(text):
    """
    Lista todas as informações visíveis a partir do texto extraído.
    Remove linhas vazias e espaços extras.
    """
    lines = text.splitlines()
    information = [line.strip() for line in lines if line.strip()]
    return information
