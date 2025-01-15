import re
from .google_vision import google_vision_extract

def listar_informacoes_visiveis(texto):
    """Lista todas as informações visíveis no texto extraído."""
    linhas = texto.splitlines()
    informacoes = [linha.strip() for linha in linhas if linha.strip()]
    return informacoes

def organizar_informacoes_cpf(informacoes):
    """Organiza informações específicas de um CPF."""
    resultado = {
        "Nome": None,
        "CPF": None,
        "Data de Nascimento": None
    }
    for i, linha in enumerate(informacoes):
        if "NOME" in linha.upper() and i + 1 < len(informacoes):
            resultado["Nome"] = informacoes[i + 1]
        elif re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", linha):
            resultado["CPF"] = linha
        elif "NASCIMENTO" in linha.upper() and i + 1 < len(informacoes):
            resultado["Data de Nascimento"] = informacoes[i + 1]
    return {k: v for k, v in resultado.items() if v}

def organizar_informacoes_rg(informacoes):
    """Organiza informações específicas de um RG."""
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
    while i < len(informacoes):
        linha = informacoes[i]
        if "NOME" in linha.upper() and i + 1 < len(informacoes):
            # Captura nomes válidos, ignorando palavras-chave irrelevantes
            nome_possivel = informacoes[i + 1]
            if re.match(r"^[A-Za-zÀ-Ü\s]+$", nome_possivel) and "FILIAÇÃO" not in nome_possivel.upper():
                resultado["Nome"] = nome_possivel
            i += 1
        elif "CPF" in linha.upper() and i + 1 < len(informacoes):
            cpf_match = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", linha + " " + informacoes[i + 1])
            if cpf_match:
                resultado["CPF"] = cpf_match.group(0)
            i += 1
        elif "REGISTRO" in linha.upper() and i + 1 < len(informacoes):
            rg_match = re.search(r"\d{2}\.\d{3}\.\d{3}-\d{1}", linha + " " + informacoes[i + 1])
            if rg_match:
                resultado["RG"] = rg_match.group(0)
            i += 1
        elif "DATA DE NASCIMENTO" in linha.upper() and i + 1 < len(informacoes):
            resultado["Data de Nascimento"] = informacoes[i + 1]
            i += 1
        elif "DATA DE EXPEDIÇÃO" in linha.upper() and i + 1 < len(informacoes):
            resultado["Data de Expedição"] = informacoes[i + 1]
            i += 1
        elif "FILIAÇÃO" in linha.upper() and i + 1 < len(informacoes):
            # Captura múltiplas linhas de filiação até encontrar outro campo
            i += 1
            while i < len(informacoes) and not informacoes[i].startswith(("NOME", "CPF", "NATURALIDADE", "DATA", "VALID", "CARTEIRA", "DOC ORIGEM")):
                if re.match(r"^[A-Za-zÀ-Ü\s]+$", informacoes[i]):  # Apenas nomes válidos
                    resultado["Filiação"].append(informacoes[i])
                i += 1
            i -= 1  # Regride para processar o próximo campo corretamente
        elif "NATURALIDADE" in linha.upper() and i + 1 < len(informacoes):
            resultado["Naturalidade"] = informacoes[i + 1]
            i += 1
        i += 1

    # Remove campos vazios
    resultado = {k: v for k, v in resultado.items() if v}

    return resultado




def organizar_informacoes_cnh(informacoes):
    """Organiza informações específicas de uma CNH."""
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
    while i < len(informacoes):
        linha = informacoes[i]
        if "NOME" in linha.upper() and i + 1 < len(informacoes):
            nome_possivel = informacoes[i + 1]
            # Captura o próximo valor válido mesmo após palavras genéricas
            if "DEPARTAMENTO" not in nome_possivel.upper() and "CARTEIRA" not in nome_possivel.upper():
                resultado["Nome"] = nome_possivel
            elif i + 2 < len(informacoes):  # Tenta capturar o próximo valor se o atual não for válido
                resultado["Nome"] = informacoes[i + 2]
            i += 1
        elif "DOC.IDENTIDADE" in linha.upper() and i + 1 < len(informacoes):
            resultado["Documento de Identidade"] = informacoes[i + 1]
            i += 1
        elif "CPF" in linha.upper() and i + 1 < len(informacoes):
            cpf_data = informacoes[i + 1]
            cpf_match = re.search(r"\d{3}\.\d{3}\.\d{3}-\d{2}", cpf_data)
            data_nasc_match = re.search(r"\d{2}/\d{2}/\d{4}", cpf_data)
            if cpf_match:
                resultado["CPF"] = cpf_match.group(0)
            if data_nasc_match:
                resultado["Data de Nascimento"] = data_nasc_match.group(0)
            i += 1
        elif "N° REGISTRO" in linha.upper() and i + 1 < len(informacoes):
            resultado["N° Registro"] = informacoes[i + 1]
            i += 1
        elif "VALIDADE" in linha.upper() and i + 1 < len(informacoes):
            resultado["Validade"] = informacoes[i + 1]
            i += 1
        elif "1° HABILITAÇÃO" in linha.upper() and i + 1 < len(informacoes):
            resultado["Primeira Habilitação"] = informacoes[i + 1]
            i += 1
        elif "DATA EMISSÃO" in linha.upper() and i + 1 < len(informacoes):
            resultado["Data de Emissão"] = informacoes[i + 1]
            i += 1
        elif "CATEGORIA" in linha.upper() and i + 1 < len(informacoes):
            resultado["Categoria"] = informacoes[i + 1]
            i += 1
        elif "FILIAÇÃO" in linha.upper() and i + 1 < len(informacoes):
            # Captura múltiplas linhas de filiação até encontrar outro campo
            i += 1
            while i < len(informacoes) and not informacoes[i].startswith(("NOME", "CPF", "DOC.IDENTIDADE", "VALIDADE", "1° HABILITAÇÃO", "CAT.HAB.", "N° REGISTRO", "LOCAL")):
                if not re.match(r"(- PERMISSÃO|ACC|CAT\.HAB\.)", informacoes[i].upper()):
                    resultado["Filiação"].append(informacoes[i])
                i += 1
            i -= 1  # Regride para processar o próximo campo corretamente
        elif "LOCAL" in linha.upper() and i + 1 < len(informacoes):
            if "ASSINATURA" not in informacoes[i + 1].upper():
                resultado["Local"] = informacoes[i + 1]
            i += 1
        i += 1

    # Remove campos vazios
    resultado = {k: v for k, v in resultado.items() if v}

    return resultado


def processar_documento(image_path, tipo_documento):
    """Processa uma imagem de documento para listar e organizar informações."""
    texto_extraido = google_vision_extract(image_path)
    informacoes_visiveis = listar_informacoes_visiveis(texto_extraido)

    if tipo_documento == "CPF":
        informacoes_organizadas = organizar_informacoes_cpf(informacoes_visiveis)
    elif tipo_documento == "RG":
        informacoes_organizadas = organizar_informacoes_rg(informacoes_visiveis)
    elif tipo_documento == "CNH":
        informacoes_organizadas = organizar_informacoes_cnh(informacoes_visiveis)
    else:
        informacoes_organizadas = {"Erro": "Tipo de documento inválido"}

    return {
        "Tipo de Documento": tipo_documento,
        "Informações Visíveis": informacoes_visiveis,
        "Informações Organizadas": informacoes_organizadas
    }