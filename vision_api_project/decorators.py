import json
import unicodedata
import re
from typing import Callable

def normalize_text(text):
    """Remove acentos, transforma para minúsculas e remove caracteres especiais, mantendo apenas letras e números simples."""
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")  # Remove acentos
    text = text.lower().strip()  # Converte para minúsculas e remove espaços desnecessários
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove caracteres especiais
    text = " ".join(text.split())  # Remove múltiplos espaços
    return text

def normalize_document_field(value):
    """Normaliza campos específicos como CPF, RG e locais de emissão"""
    if isinstance(value, str):
        value = normalize_text(value)
        value = re.sub(r'\s+', ' ', value)  # Remove espaços extras
        value = re.sub(r'\d+\.\d+\.\d+\-\d+', lambda x: x.group().replace(".", "").replace("-", ""), value)  # Remove pontos no CPF/RG
        return value
    elif isinstance(value, list):
        return [normalize_document_field(v) for v in value if v]  # Remove vazios
    elif isinstance(value, dict):
        return {normalize_text(k): normalize_document_field(v) for k, v in value.items()}
    return value

def normalize_json(data):
    """Normaliza todos os valores dentro de um dicionário JSON."""
    if isinstance(data, dict):
        return {normalize_text(k): normalize_document_field(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_document_field(item) for item in data if item]  # Remove campos vazios
    return normalize_document_field(data)

def vote(n: int, threshold: float = 0.4):
    """
    Decorator que executa uma função várias vezes e retorna o resultado majoritário,
    com flexibilização para aceitar opções com pelo menos `threshold` (40%) dos votos.
    """
    assert n >= 3, "O número de execuções deve ser pelo menos 3."
    assert 0 < threshold <= 1, "O threshold deve estar entre 0 e 1."
    
    def vote_decorator(f: Callable):
        def wrapper(*args, **kwargs):
            votes = []
            
            def apply_and_vote(idx: int, args: list, kwargs: dict):
                """Executa a função e adiciona o resultado normalizado à votação."""
                result = f(*args, **kwargs)
                normalized_result = normalize_json(result)  # Normaliza o resultado
                votes.append(json.dumps(normalized_result, sort_keys=True))  # Converte para string ordenada
            
            for i in range(n):
                apply_and_vote(i, args, kwargs)
            
            # Contabiliza os resultados
            groups = {}
            for result in votes:
                groups[result] = groups.get(result, 0) + 1
            
            # Ordena os resultados por frequência
            votes_results = sorted(groups.items(), key=lambda item: item[1], reverse=True)
            
            # Calcula a porcentagem do voto mais frequente
            total_votes = sum(groups.values())
            top_result, top_count = votes_results[0]
            top_percentage = top_count / total_votes

            # Se houver maioria absoluta, retorna o vencedor
            if top_percentage > 0.5:
                return json.loads(top_result)

            # Se houver pelo menos 40% dos votos, aceita como válido
            if top_percentage >= threshold:
                return json.loads(top_result)

            # Se não houver consenso, retorna o mais frequente mesmo sem maioria absoluta
            return json.loads(top_result)

        return wrapper
    return vote_decorator

