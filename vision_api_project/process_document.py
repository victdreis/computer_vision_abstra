import json
from openai import OpenAI
from .google_vision import google_vision_extract
from .utils import list_visible_information

# Load the API key from the JSON configuration file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

api_key = config["openai_api_key"]

# Configure the OpenAI API
client = OpenAI(api_key=api_key)

def gpt_extract_information(extracted_text, document_type):
    """Uses GPT to extract organized information from the extracted text."""
    if document_type == "Certidão de Casamento":
        prompt = f"""
        Extraia as seguintes informações de uma certidão de casamento com base no texto abaixo:
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
        """
    elif document_type == "Certidão de Nascimento":
        prompt = f"""
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
        """
    elif document_type == "CNH":
        prompt = f"""
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
    elif document_type == "Comprovante de Endereço":
        prompt = f"""
        Extraia as seguintes informações de um comprovante de endereço com base no texto abaixo:
        - Nome completo do titular do comprovante
        - Endereço completo (incluindo rua, número, bairro, cidade, estado e CEP)

        Texto do comprovante:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome Completo": "",
            "Endereço Completo": ""
        }}
        """
    elif document_type == "CTPS":
        prompt = f"""
        Extraia as seguintes informações de uma CTPS (Carteira de Trabalho e Previdência Social) com base no texto abaixo:
        - Nome completo do titular
        - Ocupação atual (cargo ou função descrito no documento)
        - Remunerações (valores salariais mencionados, incluindo períodos de pagamento)

        Texto da CTPS:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "Ocupação": "",
            "Remunerações": [
                {{
                    "Período": "",
                    "Valor": ""
                }}
            ]
        }}
        """
    elif document_type == "Holerite":
        prompt = f"""
        Extraia as seguintes informações de um holerite com base no texto abaixo:
        - Nome do funcionário
        - Salário base
        - Descontos
        - Valor líquido

        Texto do holerite:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "Salário Base": "",
            "Descontos": "",
            "Valor Líquido": ""
        }}
        """
    elif document_type == "Imposto de Renda":
        prompt = f"""
        Extraia as seguintes informações de um documento de Imposto de Renda com base no texto abaixo:
        - Nome do declarante
        - CPF do declarante
        - Natureza do rendimento
        - Valor dos rendimentos

        Texto do documento:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "CPF": "",
            "Natureza do Rendimento": "",
            "Valor dos Rendimentos": ""
        }}
        """
    elif document_type == "FGTS":
        prompt = f"""
        Extraia as seguintes informações de um documento do FGTS com base no texto abaixo:
        - Nome do trabalhador
        - Nome das empresas
        - Valores depositados por cada empresa

        Texto do documento:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "Empresas": [
                {{
                    "Empresa": "",
                    "Valor Depositado": ""
                }}
            ]
        }}
        """
    else:
        # Default for generic documents
        prompt = f"""
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
        """

    # Make the request to GPT
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an assistant that organizes document information."},
            {"role": "user", "content": prompt}
        ]
    )

    # Return the processed response
    return json.loads(response.choices[0].message.content)


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
