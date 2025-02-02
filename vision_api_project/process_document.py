import json
from openai import OpenAI
from .google_vision import google_vision_extract
from .utils import list_visible_information
from .decorators import vote

# Load the API key from the JSON configuration file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

api_key = config["openai_api_key"]

# Configure the OpenAI API
client = OpenAI(api_key=api_key)

def gpt_extract_information(extracted_text, document_type):
    """Uses GPT to extract structured information from the given text."""
    
    prompts = {
        "Certidão de Casamento": f"""
        Extraia as seguintes informações de uma Certidão de Casamento com base no texto abaixo:
        - Nome dos noivos
        - Data do casamento
        - Regime de bens
        - Nome alterado (se algum dos noivos mudou de nome após o casamento)
        - Estado civil antes do casamento (solteiro, divorciado, etc.)

        Texto da certidão:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome dos Noivos": ["Noivo", "Noiva"],
            "Data do Casamento": "",
            "Regime de Bens": "",
            "Nome Alterado": ["Nome anterior -> Nome atual"],
            "Estado Civil Antes do Casamento": ["Estado civil do Noivo", "Estado civil da Noiva"]
        }}
        """,
        "Certidão de Nascimento": f"""
        Extraia as seguintes informações de uma Certidão de Nascimento com base no texto abaixo:
        - Nome do titular do documento
        - Data de nascimento
        - Naturalidade
        - Filiação (nome do pai e da mãe, se disponíveis)

        Texto da certidão:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "Data de Nascimento": "",
            "Naturalidade": "",
            "Filiação": ["Nome do Pai", "Nome da Mãe"]
        }}
        """,
        "CNH": f"""
        Extraia as seguintes informações de uma CNH (Carteira Nacional de Habilitação) com base no texto abaixo:
        - Nome completo
        - RG
        - CPF
        - Filiação (nomes do pai e da mãe)
        - Data de validade da CNH
        - Local de emissão

        Texto da CNH:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "RG": "",
            "CPF": "",
            "Filiação": ["Nome do Pai", "Nome da Mãe"],
            "Validade": "",
            "Local de Emissão": ""
        }}
        """
    }

    # Default for unknown document types
    prompt = prompts.get(document_type, f"""
    Extraia as seguintes informações de um documento do tipo {document_type} com base no texto abaixo:
    - Nome
    - CPF
    - RG
    - Data de Nascimento
    - Data de Expedição
    - Naturalidade
    - Filiação (nome do pai e da mãe, se disponíveis)

    Texto do documento:
    {extracted_text}

    Responda em JSON com o formato:
    {{
        "Nome": "",
        "CPF": "",
        "RG": "",
        "Data de Nascimento": "",
        "Data de Expedição": "",
        "Naturalidade": "",
        "Filiação": ["Nome do Pai", "Nome da Mãe"]
    }}
    """)

    # Make the request to GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant that organizes document information."},
            {"role": "user", "content": prompt}
        ]
    )

    # Return the processed response
    return json.loads(response.choices[0].message.content)

def extract_text(image_path):
    """Extracts visible text from an image using Google Vision."""
    extracted_text = google_vision_extract(image_path)
    return "\n".join(list_visible_information(extracted_text))

def process_document(image_path, document_type):
    """
    Processes a document image to extract structured information.
    
    Steps:
    1. Extract text from the image using Google Vision.
    2. Organize the extracted text using GPT.
    3. Return both the raw extracted text and the structured data.
    """
    try:
        # Extract visible text
        extracted_text = extract_text(image_path)

        # Check if extracted text is empty; apply voting mechanism only if needed
        if not extracted_text.strip():
            print("⚠️ Warning: Extracted text is empty. Applying voting mechanism to improve results.")
            extracted_text = vote(5)(extract_text)(image_path)

        # Process the extracted text with GPT
        organized_data = gpt_extract_information(extracted_text, document_type)

        # Return structured data
        return {
            "Document Type": document_type,
            "Visible Text": extracted_text,
            "Structured Information": organized_data
        }
    except Exception as e:
        return {
            "Error": f"An error occurred while processing the document: {e}"
        }
