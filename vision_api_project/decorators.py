import json
import unicodedata
import re
from typing import Callable
from collections import Counter
from difflib import SequenceMatcher

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

def similarity(a, b):
    """Calcula similaridade entre dois textos normalizados."""
    return SequenceMatcher(None, a, b).ratio()

def has_valid_data(json_data):
    """Verifica se o JSON possui pelo menos um campo relevante preenchido."""
    if not json_data or not isinstance(json_data, dict):
        return False
    return any(json_data.values())  # Retorna True se houver algum campo não vazio

def vote(n: int, threshold: float = 0.3):
    """
    Decorator que executa uma função várias vezes e retorna o resultado mais coerente.
    
    📌 Melhorias nesta versão:
    - **Aceita opções com pelo menos 30% dos votos**, aumentando flexibilidade.
    - **Se não atingir 30%, escolhe o JSON mais próximo do mais votado**.
    - **Evita JSONs vazios**, garantindo ao menos um campo válido.
    - **Aumenta a chance de recuperar documentos problemáticos.**
    
    🔹 Reduz descartes e melhora coerência dos resultados.
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
                
                if has_valid_data(normalized_result):  # Apenas adiciona se houver dados válidos
                    votes.append(json.dumps(normalized_result, sort_keys=True))  # Converte para string ordenada
            
            for i in range(n):
                apply_and_vote(i, args, kwargs)

            if not votes:
                return {}  # Retorna JSON vazio se não houver nenhum válido

            # Contabiliza os resultados
            groups = Counter(votes)

            # Ordena por frequência
            votes_results = groups.most_common()
            
            # Calcula a porcentagem do voto mais frequente
            total_votes = sum(groups.values())
            top_result, top_count = votes_results[0]
            top_percentage = top_count / total_votes

            # Se houver maioria absoluta (>50%), retorna o resultado
            if top_percentage > 0.5:
                return json.loads(top_result)

            # Se houver pelo menos 30% dos votos, aceita como válido
            if top_percentage >= threshold:
                return json.loads(top_result)

            # Se não houver consenso, escolhe a opção mais similar à mais votada
            best_match = max(votes_results, key=lambda item: similarity(item[0], top_result))
            return json.loads(best_match[0])

        return wrapper
    return vote_decorator
