# decorators.py
import json
from typing import Callable

def vote(n: int):
    """Decorator that runs a function multiple times and returns the majority result."""
    assert n >= 3, "Number of votes should be at least 3."
    
    def vote_decorator(f: Callable):
        def wrapper(*args, **kwargs):
            votes = []
            
            def apply_and_vote(idx: int, args: list, kwargs: dict):
                result = f(*args, **kwargs)
                votes.append(result)
            
            for i in range(n):
                apply_and_vote(i, args, kwargs)
            
            # Count occurrences of each result
            groups = {}
            for result in votes:
                key = json.dumps(result, sort_keys=True)  # Convert to string for comparison
                groups[key] = groups.get(key, 0) + 1
            
            # Sort results by frequency
            votes_results = sorted(groups.items(), key=lambda item: item[1], reverse=True)
            
            # Ensure a majority exists
            assert votes_results[0][1] > n // 2, f"No majority vote for {f.__name__}. Results: {groups}"
            
            return json.loads(votes_results[0][0])  # Convert back to dict
        
        return wrapper
    return vote_decorator
