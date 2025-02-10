from openai import OpenAI
from .google_vision import google_vision_extract
from .utils import list_visible_information
from .decorators import vote, has_valid_data  
import json

# Load the API key from the JSON configuration file
with open("config.json", "r") as config_file:
    config = json.load(config_file)

api_key = config["openai_api_key"]

# Configure the OpenAI API
client = OpenAI(api_key=api_key)

import json
from openai import OpenAI

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
        - Filiação (pai e mãe)
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
        """,

        "RG": f"""
        Extraia as seguintes informações de um RG (Registro Geral) com base no texto abaixo:
        - Nome completo
        - RG
        - CPF (se disponível)
        - Data de nascimento
        - Naturalidade
        - Filiação (pai e mãe)

        Texto do RG:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "RG": "",
            "CPF": "",
            "Data de Nascimento": "",
            "Naturalidade": "",
            "Filiação": ["Nome do Pai", "Nome da Mãe"]
        }}
        """,

        "CPF": f"""
        Extraia as seguintes informações de um CPF com base no texto abaixo:
        - Nome completo
        - CPF
        - Data de nascimento

        Texto do CPF:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "CPF": "",
            "Data de Nascimento": ""
        }}
        """,

        "Comprovante de Endereço": f"""
        Extraia as seguintes informações de um comprovante de endereço com base no texto abaixo:
        - Nome do titular do comprovante
        - Endereço completo (incluindo rua, número, bairro, cidade, estado e CEP)

        Texto do comprovante de endereço:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome Completo": "",
            "Endereço Completo": ""
        }}
        """,

        "CTPS": f"""
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
        """,

        "Holerite": f"""
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
        """,

        "Imposto de Renda": f"""
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
        """,

        "Driver's License": f"""
        Extraia as seguintes informações de um documento de Driver's License com base no texto abaixo:
        - Nome
        - Número da CNH
        - Data de Nascimento
        - Endereço
        - Classe
        - Data de Expiração
        - Data de Emissão
        - Altura
        - Sexo
        - Cor dos Olhos

        Texto do documento:
        {extracted_text}

        Responda em JSON com o formato:
        {{
            "Nome": "",
            "Número da CNH": "",
            "Data de Nascimento": "",
            "Endereço": "",
            "Classe": "",
            "Data de Expiração": "",
            "Data de Emissão": "",
            "Altura": "",
            "Sexo": "",
            "Cor dos Olhos": ""
        }}
        """,

        "FGTS": f"""
        Extraia as seguintes informações de um extrato do FGTS com base no texto abaixo:
        - Nome do trabalhador
        - Nome das empresas onde o trabalhador teve vínculo
        - Valores depositados por cada empresa

        Texto do extrato do FGTS:
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
    }

    prompt = prompts.get(document_type, f"""
    Extraia as seguintes informações de um documento do tipo {document_type} com base no texto abaixo:
    - Nome
    - CPF
    - RG
    - Data de Nascimento
    - Data de Expedição
    - Naturalidade
    - Filiação (pai e mãe)

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

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are an AI assistant that organizes document information."},
            {"role": "user", "content": prompt}
        ]
    )

    return json.loads(response.choices[0].message.content)


def extract_text(image_path):
    """Extracts visible text from an image using Google Vision."""
    extracted_text = google_vision_extract(image_path)
    print(f"🔍 Extracted text: {extracted_text}")  # DEBUG: Verifique se algo está sendo extraído
    return "\n".join(list_visible_information(extracted_text))


def process_document(image_path, document_type):
    """
    Processes a document image to extract structured information.
    """
    try:
        # Extract visible text
        extracted_text = extract_text(image_path)
        print(f"📝 DEBUG: Texto extraído: {extracted_text}")

        # Apply voting mechanism if needed
        if not extracted_text.strip():
            print("⚠️ DEBUG: Texto extraído está vazio. Aplicando mecanismo de votação.")
            extracted_text = vote(5)(extract_text)(image_path)

        # Process the extracted text with GPT
        organized_data = gpt_extract_information(extracted_text, document_type)

        # Prepare final JSON
        final_result = {
            "Tipo de Documento": document_type,
            "Texto Visível": extracted_text,
            "Informações Organizadas": organized_data
        }

        print(f"✅ DEBUG: JSON final retornado:\n{json.dumps(final_result, indent=4, ensure_ascii=False)}")
        return final_result

    except Exception as e:
        print(f"❌ DEBUG: Erro no process_document: {e}")
        return
