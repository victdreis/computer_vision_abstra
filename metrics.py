import os
import json
import unicodedata
from difflib import SequenceMatcher

def clean_text(text):
    """Normalizes the text by removing accents, extra spaces, and converting to lowercase."""
    if not text:
        return ""
    text = text.lower().strip()
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))  # Removes accents
    text = " ".join(text.split())  # Removes extra spaces
    return text

def similar(a, b):
    """Checks similarity between two texts using SequenceMatcher."""
    return SequenceMatcher(None, a, b).ratio()

def extract_ground_truth_text(txt_path):
    """Extracts ground truth values from the TXT file and normalizes them."""
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    
    transcriptions = [line.split(",")[-1].strip() for line in lines if "," in line]
    return set(clean_text(t) for t in transcriptions)  # Normalize for comparison

def check_field_accuracy(organized_info, ground_truth_text):
    """Checks if extracted fields match those in the ground truth using similarity comparison."""
    results = {}
    total_fields = 0
    matched_fields = 0
    similarity_threshold = 0.85  # Reduced threshold for better flexibility

    for key, value in organized_info.items():
        if isinstance(value, list):
            sub_results = []
            for item in value:
                total_fields += 1
                normalized_item = clean_text(item)
                matched = any(similar(normalized_item, clean_text(gt)) >= similarity_threshold for gt in ground_truth_text)
                sub_results.append({"value": item, "matched": matched})
                if matched:
                    matched_fields += 1
            results[key] = sub_results
        else:
            total_fields += 1
            normalized_value = clean_text(value)
            matched = any(similar(normalized_value, clean_text(gt)) >= similarity_threshold for gt in ground_truth_text)
            results[key] = {"value": value, "matched": matched}
            if matched:
                matched_fields += 1

    accuracy = matched_fields / total_fields if total_fields > 0 else 0
    return results, accuracy

if __name__ == "__main__":
    # Define directories
    data_dirs = {"CNH_Aberta": "data/CNH_Aberta", "RG_Aberto": "data/RG_Aberto"}
    results_dir = "results"
    summary = {}

    total_files = 0
    processed_files = 0
    failed_files = []  # List to store failed files

    document_stats = {  # Tracking stats for each document type
        "CNH_Aberta": {"total": 0, "processed": 0},
        "RG_Aberto": {"total": 0, "processed": 0}
    }

    for sub_dir, data_path in data_dirs.items():
        results_path = os.path.join(results_dir, sub_dir)

        if not os.path.exists(results_path):
            print(f"❌ Diretório não encontrado: {results_path}. Pulando.")
            continue

        print(f"🔍 Processando diretório: {results_path}")

        for file_name in os.listdir(results_path):
            if file_name.endswith(".json"):
                total_files += 1
                document_stats[sub_dir]["total"] += 1  # Count total files per document type
                
                json_output_file = os.path.join(results_path, file_name)
                base_name = file_name.replace(".json", "")
                txt_file = os.path.join(data_path, f"{base_name}_gt_ocr.txt")

                if not os.path.exists(txt_file):
                    print(f"⚠️ Arquivo ground truth não encontrado para {file_name}. Pulando.")
                    failed_files.append(file_name)
                    continue

                try:
                    # Load extracted JSON
                    with open(json_output_file, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                        extracted_info = json_data.get("Informações Organizadas", {})

                    if not extracted_info:
                        print(f"⚠️ JSON {file_name} está vazio. Pulando.")
                        failed_files.append(file_name)
                        continue

                    # Extract ground truth text
                    ground_truth_text = extract_ground_truth_text(txt_file)

                    # Calculate accuracy
                    field_results, overall_accuracy = check_field_accuracy(extracted_info, ground_truth_text)

                    # Update JSON with results
                    json_data["overall_accuracy"] = overall_accuracy
                    json_data["field_results"] = field_results

                    # Save updated JSON
                    with open(json_output_file, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)

                    print(f"✅ Atualizado {file_name} com acurácia: {overall_accuracy:.2%}")
                    
                    if sub_dir not in summary:
                        summary[sub_dir] = []
                    summary[sub_dir].append({"file_name": file_name, "accuracy": overall_accuracy})
                    
                    processed_files += 1
                    document_stats[sub_dir]["processed"] += 1  # Count processed files per document type

                except Exception as e:
                    print(f"❌ Erro ao calcular a acurácia para {file_name}: {e}")
                    failed_files.append(file_name)

    # Calculate percentage of processed files
    processed_percentage = (processed_files / total_files) * 100 if total_files > 0 else 0

    # Calculate individual success rates
    cnh_success_rate = (document_stats["CNH_Aberta"]["processed"] / document_stats["CNH_Aberta"]["total"]) * 100 if document_stats["CNH_Aberta"]["total"] > 0 else 0
    rg_success_rate = (document_stats["RG_Aberto"]["processed"] / document_stats["RG_Aberto"]["total"]) * 100 if document_stats["RG_Aberto"]["total"] > 0 else 0

    # Save final summary
    summary_file = os.path.join(results_dir, "summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "average_accuracy": sum(x["accuracy"] for doc in summary.values() for x in doc) / processed_files if processed_files > 0 else 0,
            "processed_percentage": processed_percentage,
            "total_files": total_files,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "document_results": summary,
            "CNH_success_rate": cnh_success_rate,
            "RG_success_rate": rg_success_rate
        }, f, ensure_ascii=False, indent=4)

    print(f"📊 Resumo salvo em {summary_file}")
    print(f"📈 {processed_percentage:.2f}% dos documentos foram processados com sucesso ({processed_files}/{total_files}).")
    print(f"📌 Sucesso CNH: {cnh_success_rate:.2f}% | Sucesso RG: {rg_success_rate:.2f}%")

    # Display failed files
    if failed_files:
        print("\n⚠️ Arquivos que não puderam ser processados:")
        for file in failed_files:
            print(f"   ❌ {file}")
