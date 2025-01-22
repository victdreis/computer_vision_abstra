import re
from .google_vision import google_vision_extract
from .utils import google_nlp_analyze_entities, list_visible_information

# Funções auxiliares
def is_valid_name(text):
    """Check if a text is a valid name."""
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", text)) and len(text.split()) > 1

def extract_field(pattern, text):
    """Extract a field from text using a regex pattern."""
    match = re.search(pattern, text)
    return match.group(0) if match else None

# Funções específicas para documentos
def process_rg_cnh(visible_information):
    """Processa RG e CNH para verificar dados legíveis."""
    data = {
        "RG": None,
        "CPF": None,
        "Data de Expedição": None
    }
    
    for line in visible_information:
        if not data["CPF"]:
            data["CPF"] = extract_field(r"\d{3}\.\d{3}\.\d{3}-\d{2}", line)
        if not data["RG"]:
            data["RG"] = extract_field(r"\d{2}\.\d{3}\.\d{3}-\d{1}", line)
        if not data["Data de Expedição"]:
            data["Data de Expedição"] = extract_field(r"\d{2}/\d{2}/\d{4}", line)
    
    return data

def process_certidao_nascimento(visible_information):
    """Processa certidão de nascimento para estado civil, cidade e estado de nascimento."""
    data = {
        "Estado Civil": None,
        "Naturalidade": None
    }
    
    for line in visible_information:
        if "SOLTEIRO" in line.upper() and not data["Estado Civil"]:
            data["Estado Civil"] = "Solteiro"
        if "NATURALIDADE" in line.upper() and not data["Naturalidade"]:
            data["Naturalidade"] = line.split(":")[-1].strip()
    
    return data

def process_certidao_casamento(visible_information):
    """Processa certidão de casamento para estado civil, nome atual e regime."""
    data = {
        "Estado Civil": None,
        "Nome Atual": None,
        "Regime de Casamento": None
    }

    for line in visible_information:
        if "DIVÓRCIO" in line.upper():
            data["Estado Civil"] = "Divorciado"
        elif "CASADO" in line.upper():
            data["Estado Civil"] = "Casado"
        if "PASSOU A ASSINAR" in line.upper():
            data["Nome Atual"] = extract_field(r"PASSOU A ASSINAR:\s*(.+)", line)
        if "REGIME" in line.upper():
            if "COMUNHÃO PARCIAL" in line.upper():
                data["Regime de Casamento"] = "Comunhão Parcial - APTO"
            elif "COMUNHÃO TOTAL" in line.upper():
                data["Regime de Casamento"] = "Comunhão Total - APTO"
            elif "SEPARAÇÃO TOTAL" in line.upper():
                if "PACTO" in line.upper():
                    data["Regime de Casamento"] = "Separação Total - Pacto Requerido"
                else:
                    data["Regime de Casamento"] = "Separação Total"

    return data

def process_comprovante_endereco(visible_information):
    """Processa comprovante de endereço para validar dados."""
    data = {
        "Validade": "Inapto",
        "Região Limítrofe": None
    }

    for line in visible_information:
        if "60 DIAS" in line.upper():
            data["Validade"] = "Apto"
        if "REGIÃO LIMÍTROFE" in line.upper():
            data["Região Limítrofe"] = line.split(":")[-1].strip()

    return data

def process_default(visible_information):
    """Processa documentos não específicos imprimindo todo o texto visível."""
    return {"Texto Visível": "\n".join(visible_information)}

# Função principal
def process_document(image_path, document_type):
    """Processa o documento baseado no tipo especificado."""
    extracted_text = google_vision_extract(image_path)
    visible_information = list_visible_information(extracted_text)

    if document_type == "RG ou CNH":
        return process_rg_cnh(visible_information)
    elif document_type == "Certidão de Nascimento":
        return process_certidao_nascimento(visible_information)
    elif document_type == "Certidão de Casamento":
        return process_certidao_casamento(visible_information)
    elif document_type == "Comprovante de Endereço":
        return process_comprovante_endereco(visible_information)
    else:
        return process_default(visible_information)
