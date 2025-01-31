import json
from openai import OpenAI
from .google_vision import google_vision_extract
from .utils import list_visible_information
from .decorators import vote  # Importando o decorador

# Load the API key from the JSON configuration file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

api_key = config["openai_api_key"]
client = OpenAI(api_key=api_key)

def gpt_extract_information(extracted_text, document_type):
    """Uses GPT to extract organized information from the extracted text."""
    
    # Define different prompts based on document type
    prompts = {
        "Certidão de Casamento": f"""
            Extraia as seguintes informações de uma certidão de casamento:
            - Nome dos noivos
            - Data do casamento
            - Regime de bens
            - Nome alterado (se houve mudança)
            - Estado civil antes do casamento
            
            Texto da certidão:
            {extracted_text}
            
            Responda em JSON:
            {{
                "Nome dos Noivos": ["", ""],
                "Data do Casamento": "",
                "Regime de Bens": "",
                "Nome Alterado": ["", ""],
                "Estado Civil Antes do Casamento": ["", ""]
            }}
        """,
        "Certidão de Nascimento": f"""
            Extraia informações de uma Certidão de Nascimento:
            - Nome do titular
            - Data de nascimento
            - Naturalidade
            - Filiação
            
            Texto da certidão:
            {extracted_text}
            
            Responda em JSON:
            {{
                "Nome": "",
                "Data de Nascimento": "",
                "Naturalidade": "",
                "Filiação": ["", ""]
            }}
        """,
        "CNH": f"""
            Extraia informações de uma CNH:
            - Nome completo
            - RG, CPF
            - Filiação (pai e mãe)
            - Data de validade
            - Local de emissão
            
            Texto da CNH:
            {extracted_text}
            
            Responda em JSON:
            {{
                "Nome": "",
                "RG": "",
                "CPF": "",
                "Filiação": ["", ""],
                "Validade": "",
                "Local de Emissão": ""
            }}
        """
    }

    prompt = prompts.get(document_type, f"""
        Extraia informações de um documento tipo {document_type}:
        - Nome
        - CPF, RG
        - Data de Nascimento
        - Naturalidade
        - Filiação

        Texto:
        {extracted_text}

        Responda em JSON:
        {{
            "Nome": "",
            "CPF": "",
            "RG": "",
            "Data de Nascimento": "",
            "Naturalidade": "",
            "Filiação": ["", ""]
        }}
    """)

    # Make the request to GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Você é um assistente que organiza informações de documentos."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)

@vote(5)  # O decorador executa a função 5 vezes e retorna o resultado majoritário
def process_document(image_path, document_type):
    """Processes a document image to extract and organize information."""
    try:
        # Extract visible text from the image
        extracted_text = google_vision_extract(image_path)
        visible_information = "\n".join(list_visible_information(extracted_text))

        # Use GPT to organize the information
        organized_data = gpt_extract_information(visible_information, document_type)

        # Return the organized data along with visible text
        return {
            "Tipo de Documento": document_type,
            "Texto Visível": visible_information,
            "Informações Organizadas": organized_data
        }
    except Exception as e:
        return {
            "Erro": f"Ocorreu um erro ao processar o documento: {e}"
        }

# Teste opcional para verificar se o decorador funciona
if __name__ == "__main__":
    test_result = process_document("caminho_para_um_teste.jpg", "CNH")
    print(json.dumps(test_result, indent=4, ensure_ascii=False))
