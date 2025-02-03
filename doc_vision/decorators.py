import json
import unicodedata
import re
from typing import Callable
from collections import Counter
from difflib import SequenceMatcher

def normalize_text(text):
    """
    Removes accents, converts to lowercase, and removes special characters,
    keeping only alphanumeric characters and spaces.
    
    Args:
        text (str): Input text to be normalized.
    
    Returns:
        str: Normalized text.
    """
    if not isinstance(text, str):
        return text
    text = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("ASCII")  # Remove accents
    text = text.lower().strip()  # Convert to lowercase and remove unnecessary spaces
    text = re.sub(r'[^a-z0-9\s]', '', text)  # Remove special characters
    text = " ".join(text.split())  # Remove multiple spaces
    return text

def normalize_document_field(value):
    """
    Normalizes specific document fields like CPF, RG, and issuance locations.
    
    Args:
        value (str, list, dict): The document field value to be normalized.
    
    Returns:
        The normalized value with cleaned formatting.
    """
    if isinstance(value, str):
        value = normalize_text(value)
        value = re.sub(r'\s+', ' ', value)  # Remove extra spaces
        value = re.sub(r'\d+\.\d+\.\d+\-\d+', lambda x: x.group().replace(".", "").replace("-", ""), value)  # Remove CPF/RG dots
        return value
    elif isinstance(value, list):
        return [normalize_document_field(v) for v in value if v]  # Remove empty values
    elif isinstance(value, dict):
        return {normalize_text(k): normalize_document_field(v) for k, v in value.items()}
    return value

def normalize_json(data):
    """
    Normalizes all values within a JSON dictionary.
    
    Args:
        data (dict or list): JSON-like structure containing text data.
    
    Returns:
        The normalized JSON structure.
    """
    if isinstance(data, dict):
        return {normalize_text(k): normalize_document_field(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [normalize_document_field(item) for item in data if item]  # Remove empty fields
    return normalize_document_field(data)

def similarity(a, b):
    """
    Computes similarity between two normalized texts.
    
    Args:
        a (str): First text.
        b (str): Second text.
    
    Returns:
        float: Similarity ratio between 0 and 1.
    """
    return SequenceMatcher(None, a, b).ratio()

def has_valid_data(json_data):
    """
    Checks if the JSON contains at least one relevant non-empty field.
    
    Args:
        json_data (dict): JSON structure to be validated.
    
    Returns:
        bool: True if at least one field is non-empty, False otherwise.
    """
    if not json_data or not isinstance(json_data, dict):
        return False
    return any(json_data.values())  # Returns True if any field is non-empty

def vote(n: int, threshold: float = 0.3):
    """
    Decorator that runs a function multiple times and returns the most consistent result.
    
    Improvements in this version:
    - Accepts results with at least 30% of votes, increasing flexibility.
    - If no result reaches 30%, selects the JSON most similar to the most voted one.
    - Avoids empty JSONs, ensuring at least one valid field.
    - Increases the chance of recovering problematic documents.
    
    Reduces discards and improves consistency of results.
    
    Args:
        n (int): Number of times the function should be executed.
        threshold (float): Minimum percentage required for a result to be considered valid.
    
    Returns:
        Callable: The decorated function.
    """
    assert n >= 3, "The number of executions must be at least 3."
    assert 0 < threshold <= 1, "The threshold must be between 0 and 1."
    
    def vote_decorator(f: Callable):
        def wrapper(*args, **kwargs):
            votes = []
            
            def apply_and_vote(idx: int, args: list, kwargs: dict):
                """Executes the function and adds the normalized result to the voting pool."""
                result = f(*args, **kwargs)
                normalized_result = normalize_json(result)  # Normalize the result
                
                if has_valid_data(normalized_result):  # Only add if it has valid data
                    votes.append(json.dumps(normalized_result, sort_keys=True))  # Convert to sorted JSON string
            
            for i in range(n):
                apply_and_vote(i, args, kwargs)

            if not votes:
                return {}  # Return empty JSON if no valid data

            # Count occurrences of results
            groups = Counter(votes)

            # Sort by frequency
            votes_results = groups.most_common()
            
            # Compute the percentage of the most frequent vote
            total_votes = sum(groups.values())
            top_result, top_count = votes_results[0]
            top_percentage = top_count / total_votes

            # If majority (>50%) is found, return the result
            if top_percentage > 0.5:
                return json.loads(top_result)

            # If at least 30% agreement, accept as valid
            if top_percentage >= threshold:
                return json.loads(top_result)

            # If no consensus, choose the most similar result to the top vote
            best_match = max(votes_results, key=lambda item: similarity(item[0], top_result))
            return json.loads(best_match[0])

        return wrapper
    return vote_decorator