# Importações necessárias
import re
from .google_vision import google_vision_extract
from .utils import google_nlp_analyze_entities, list_visible_information

def is_valid_name(text):
    """Check if a text is a valid name."""
    return bool(re.match(r"^[A-Za-zÀ-ÖØ-öø-ÿ\s]+$", text)) and len(text.split()) > 1

def extract_field(pattern, text):
    """Extract a field from text using a regex pattern."""
    match = re.search(pattern, text)
    return match.group(0) if match else None

def organize_information(visible_information, nlp_entities):
    """Organize fields using both visible information and NLP entities."""
    organized_data = {
        "Nome": None,
        "CPF": None,
        "RG": None,
        "Data de Nascimento": None,
        "Data de Expedição": None,
        "Naturalidade": None,
        "Filiação": [],
    }

    # Extract CPF and RG
    for line in visible_information:
        if not organized_data["CPF"]:
            organized_data["CPF"] = extract_field(r"\d{3}\.\d{3}\.\d{3}-\d{2}", line)
        if not organized_data["RG"]:
            organized_data["RG"] = extract_field(r"\d{2}\.\d{3}\.\d{3}-\d{1}", line)

    # Extract other fields using proximity-based heuristics
    for i, line in enumerate(visible_information):
        line_upper = line.upper()
        if "NOME" in line_upper and not organized_data["Nome"]:
            possible_name = visible_information[i + 1] if i + 1 < len(visible_information) else None
            if possible_name and is_valid_name(possible_name):
                organized_data["Nome"] = possible_name
        elif "DATA DE NASCIMENTO" in line_upper and not organized_data["Data de Nascimento"]:
            organized_data["Data de Nascimento"] = extract_field(r"\d{2}/\d{2}/\d{4}", line)
        elif "DATA DE EXPEDIÇÃO" in line_upper and not organized_data["Data de Expedição"]:
            organized_data["Data de Expedição"] = extract_field(r"\d{2}/\d{2}/\d{4}", line)
        elif "NATURALIDADE" in line_upper and not organized_data["Naturalidade"]:
            organized_data["Naturalidade"] = visible_information[i + 1] if i + 1 < len(visible_information) else None
        elif "FILIAÇÃO" in line_upper:
            for j in range(i + 1, len(visible_information)):
                if is_valid_name(visible_information[j]):
                    organized_data["Filiação"].append(visible_information[j])
                else:
                    break

    # Use NLP entities for validation and enhancement
    for entity, entity_type in nlp_entities.items():
        if entity_type == "PERSON":
            if not organized_data["Nome"]:
                organized_data["Nome"] = entity
            elif entity not in organized_data["Filiação"]:
                organized_data["Filiação"].append(entity)
        elif entity_type == "LOCATION" and not organized_data["Naturalidade"]:
            organized_data["Naturalidade"] = entity

    # Remove duplicates and ensure valid names in Filiação
    organized_data["Filiação"] = list(set(organized_data["Filiação"]))
    organized_data["Filiação"] = [name for name in organized_data["Filiação"] if is_valid_name(name)]

    return {k: v for k, v in organized_data.items() if v}

def process_document(image_path, document_type):
    """Processes a document image to extract and organize information."""
    extracted_text = google_vision_extract(image_path)
    visible_information = list_visible_information(extracted_text)
    nlp_entities = google_nlp_analyze_entities(extracted_text)
    organized_data = organize_information(visible_information, nlp_entities)

    return {
        "Tipo de Documento": document_type,
        #"Informações Visíveis": visible_information,
        #"Entidades NLP": nlp_entities,
        "Informações Organizadas": organized_data
    }
