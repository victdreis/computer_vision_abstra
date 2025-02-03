import os
import json
import unicodedata
import re
from difflib import SequenceMatcher

def clean_text(text, preserve_accents=False):
    """
    Normalizes text by removing accents (optional), special characters, extra spaces, and converting to lowercase.
    
    Args:
        text (str): The input text to be cleaned.
        preserve_accents (bool): If True, keeps accents; otherwise, removes them.
    
    Returns:
        str: The cleaned and normalized text.
    """
    if not text:
        return ""
    text = text.strip()
    if not preserve_accents:
        text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  
    text = " ".join(text.split())  
    return text.lower()

def similar(a, b):
    """
    Checks similarity between two normalized texts using SequenceMatcher.
    
    Args:
        a (str): First text.
        b (str): Second text.
    
    Returns:
        float: A similarity ratio between 0 and 1.
    """
    return SequenceMatcher(None, a, b).ratio()

def extract_ground_truth_text(txt_path):
    """
    Extracts values from a ground truth file and normalizes them.
    
    Args:
        txt_path (str): Path to the ground truth text file.
    
    Returns:
        set: A set of normalized text values from the file.
    """
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    
    transcriptions = [line.split(",")[-1].strip() for line in lines if "," in line]
    return set(clean_text(t, preserve_accents=True) for t in transcriptions)

def check_field_accuracy(organized_info, ground_truth_text):
    """
    Verifies if extracted fields match the ground truth with a flexible similarity threshold.
    
    Args:
        organized_info (dict): Extracted fields from a document.
        ground_truth_text (set): Ground truth values.
    
    Returns:
        tuple: A dictionary of matched results and the overall accuracy.
    """
    results = {}
    total_fields = 0
    matched_fields = 0
    similarity_threshold = 0.75  

    for key, value in organized_info.items():
        if isinstance(value, list):
            sub_results = []
            for item in value:
                total_fields += 1
                normalized_item = clean_text(item, preserve_accents=True)
                matched = any(similar(normalized_item, clean_text(gt, preserve_accents=True)) >= similarity_threshold for gt in ground_truth_text)
                sub_results.append({"value": item, "matched": matched})
                if matched:
                    matched_fields += 1
            results[key] = sub_results
        else:
            total_fields += 1
            normalized_value = clean_text(value, preserve_accents=True)
            matched = any(similar(normalized_value, clean_text(gt, preserve_accents=True)) >= similarity_threshold for gt in ground_truth_text)
            results[key] = {"value": value, "matched": matched}
            if matched:
                matched_fields += 1

    accuracy = matched_fields / total_fields if total_fields > 0 else 0
    return results, accuracy

if __name__ == "__main__":
    # Define directories
    data_dirs = {
        "CNH_Aberta": "data/CNH_Aberta",
        "RG_Aberto": "data/RG_Aberto"
    }
    results_dir = "results"
    summary = {key: [] for key in data_dirs.keys()}

    total_files = 0
    processed_files = 0
    failed_files = []
    accuracy_sums = {key: 0 for key in data_dirs.keys()}
    document_stats = {key: {"total": 0, "processed": 0} for key in data_dirs.keys()}

    for sub_dir, data_path in data_dirs.items():
        results_path = os.path.join(results_dir, sub_dir)
        
        if not os.path.exists(results_path):
            print(f"❌ Directory not found: {results_path}. Skipping.")
            continue

        print(f"🔍 Processing directory: {results_path}")
        
        for file_name in os.listdir(results_path):
            if not file_name.endswith(".json"):
                continue  

            total_files += 1
            document_stats[sub_dir]["total"] += 1
            json_output_file = os.path.join(results_path, file_name)
            base_name = file_name.replace(".json", "")
            txt_file = os.path.join(data_path, f"{base_name}_gt_ocr.txt")

            if not os.path.exists(txt_file):
                print(f"⚠️ Missing ground truth for {file_name}. Logging as error.")
                failed_files.append({"file_name": file_name, "error": "Ground truth missing"})
                continue

            try:
                with open(json_output_file, "r", encoding="utf-8") as f:
                    json_data = json.load(f)
                    extracted_info = json_data.get("Informações Organizadas", {})

                if not extracted_info:
                    print(f"⚠️ JSON {file_name} is empty or lacks expected fields. Logging as error.")
                    failed_files.append({"file_name": file_name, "error": "JSON missing organized information"})
                    continue

                ground_truth_text = extract_ground_truth_text(txt_file)
                field_results, overall_accuracy = check_field_accuracy(extracted_info, ground_truth_text)

                json_data["overall_accuracy"] = overall_accuracy
                json_data["field_results"] = field_results

                with open(json_output_file, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=4)

                print(f"✅ {file_name} updated with accuracy: {overall_accuracy:.2%}")
                summary[sub_dir].append({"file_name": file_name, "accuracy": overall_accuracy})
                accuracy_sums[sub_dir] += overall_accuracy
                processed_files += 1
                document_stats[sub_dir]["processed"] += 1
            
            except Exception as e:
                print(f"❌ Error processing {file_name}: {e}")
                failed_files.append({"file_name": file_name, "error": str(e)})