import re
from .google_vision import google_vision_extract

def list_visible_information(text):
    """Lists all visible information from the extracted text."""
    lines = text.splitlines()
    information = [line.strip() for line in lines if line.strip()]
    return information

def organize_cpf_information(information):
    """Organizes specific information for a CPF."""
    resultado = {
        "Nome": None,
        "CPF": None,
        "Data de Nascimento": None
    }
    for i, line in enumerate(information):
        if "NOME" in line.upper() and i + 1 < len(information):
            resultado["Nome"] = information[i + 1]
        elif re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", line):
            resultado["CPF"] = line
        elif "NASCIMENTO" in line.upper() and i + 1 < len(information):
            resultado["Data de Nascimento"] = information[i + 1]
    return {k: v for k, v in resultado.items() if v}

def organize_rg_information(information):
    """Organizes specific information for an RG."""
    resultado = {
        "Nome": None,
        "RG": None,
        "CPF": None,
        "Data de Nascimento": None,
        "Data de Expedição": None,
        "Filiação": [],
        "Naturalidade": None
    }

    i = 0
    while i < len(information):
        line = information[i]
        if "NOME" in line.upper() and i + 1 < len(information):
            possible_name = information[i + 1]
            if re.match(r"^[A-Za-zÀ-Ü\s]+$", possible_name) and "FILIAÇÃO" not in possible_name.upper():
                resultado["Nome"] = possible_name
            i += 1
        elif "CPF" in line.upper() and i + 1 < len(information):
            cpf_match = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", line + " " + information[i + 1])
            if cpf_match:
                resultado["CPF"] = cpf_match.group(0)
            i += 1
        elif "REGISTRO" in line.upper() and i + 1 < len(information):
            rg_match = re.search(r"\d{2}\.\d{3}\.\d{3}-\d{1}", line + " " + information[i + 1])
            if rg_match:
                resultado["RG"] = rg_match.group(0)
            i += 1
        elif "DATA DE NASCIMENTO" in line.upper() and i + 1 < len(information):
            resultado["Data de Nascimento"] = information[i + 1]
            i += 1
        elif "DATA DE EXPEDIÇÃO" in line.upper() and i + 1 < len(information):
            resultado["Data de Expedição"] = information[i + 1]
            i += 1
        elif "FILIAÇÃO" in line.upper() and i + 1 < len(information):
            i += 1
            while i < len(information) and not information[i].startswith(("NOME", "CPF", "NATURALIDADE", "DATA", "VALID", "CARTEIRA", "DOC ORIGEM")):
                if re.match(r"^[A-Za-zÀ-Ü\s]+$", information[i]):
                    resultado["Filiação"].append(information[i])
                i += 1
            i -= 1
        elif "NATURALIDADE" in line.upper() and i + 1 < len(information):
            resultado["Naturalidade"] = information[i + 1]
            i += 1
        i += 1

    resultado = {k: v for k, v in resultado.items() if v}

    return resultado

def organize_cnh_information(information):
    """Organizes specific information for a CNH."""
    resultado = {
        "Nome": None,
        "Documento de Identidade": None,
        "CPF": None,
        "N° Registro": None,
        "Data de Nascimento": None,
        "Data de Emissão": None,
        "Validade": None,
        "Categoria": None,
        "Primeira Habilitação": None,
        "Filiação": [],
        "Local": None
    }

    i = 0
    while i < len(information):
        line = information[i]
        if "NOME" in line.upper() and i + 1 < len(information):
            possible_name = information[i + 1]
            if "DEPARTAMENTO" not in possible_name.upper() and "CARTEIRA" not in possible_name.upper():
                resultado["Nome"] = possible_name
            elif i + 2 < len(information):
                resultado["Nome"] = information[i + 2]
            i += 1
        elif "DOC.IDENTIDADE" in line.upper() and i + 1 < len(information):
            resultado["Documento de Identidade"] = information[i + 1]
            i += 1
        elif "CPF" in line.upper() and i + 1 < len(information):
            cpf_data = information[i + 1]
            cpf_match = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf_data)
            dob_match = re.search(r"\d{2}/\d{2}/\d{4}", cpf_data)
            if cpf_match:
                resultado["CPF"] = cpf_match.group(0)
            if dob_match:
                resultado["Data de Nascimento"] = dob_match.group(0)
            i += 1
        elif "N° REGISTRO" in line.upper() and i + 1 < len(information):
            resultado["N° Registro"] = information[i + 1]
            i += 1
        elif "VALIDADE" in line.upper() and i + 1 < len(information):
            resultado["Validade"] = information[i + 1]
            i += 1
        elif "1° HABILITAÇÃO" in line.upper() and i + 1 < len(information):
            resultado["Primeira Habilitação"] = information[i + 1]
            i += 1
        elif "DATA EMISSÃO" in line.upper() and i + 1 < len(information):
            resultado["Data de Emissão"] = information[i + 1]
            i += 1
        elif "CATEGORIA" in line.upper() and i + 1 < len(information):
            resultado["Categoria"] = information[i + 1]
            i += 1
        elif "FILIAÇÃO" in line.upper() and i + 1 < len(information):
            i += 1
            while i < len(information) and not information[i].startswith(("NOME", "CPF", "DOC.IDENTIDADE", "VALIDADE", "1° HABILITAÇÃO", "CAT.HAB.", "N° REGISTRO", "LOCAL")):
                if not re.match(r"(- PERMISSÃO|ACC|CAT\.HAB\.)", information[i].upper()):
                    resultado["Filiação"].append(information[i])
                i += 1
            i -= 1
        elif "LOCAL" in line.upper() and i + 1 < len(information):
            if "ASSINATURA" not in information[i + 1].upper():
                resultado["Local"] = information[i + 1]
            i += 1
        i += 1

    resultado = {k: v for k, v in resultado.items() if v}

    return resultado

def process_document(image_path, document_type):
    """Processes a document image to list and organize information."""
    extracted_text = google_vision_extract(image_path)
    visible_information = list_visible_information(extracted_text)

    if document_type == "CPF":
        organized_information = organize_cpf_information(visible_information)
    elif document_type == "RG":
        organized_information = organize_rg_information(visible_information)
    elif document_type == "CNH":
        organized_information = organize_cnh_information(visible_information)
    else:
        organized_information = {"Erro": "Tipo de documento inválido"}

    return {
        "Tipo de Documento": document_type,
        "Informações Visíveis": visible_information,
        "Informações Organizadas": organized_information
    }
