import os
import json
import unicodedata
import re
from difflib import SequenceMatcher

def clean_text(text, preserve_accents=False):
    """Normaliza o texto removendo acentos (opcional), caracteres especiais, espaços extras e convertendo para minúsculas."""
    if not text:
        return ""
    text = text.strip()
    if not preserve_accents:
        text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))
    
    # Remove caracteres especiais e formatação de números
    text = re.sub(r"[^a-zA-Z0-9\s]", "", text)  
    text = " ".join(text.split())  # Remove espaços extras
    return text.lower()

def similar(a, b):
    """Verifica a similaridade entre dois textos usando SequenceMatcher."""
    return SequenceMatcher(None, a, b).ratio()

def extract_ground_truth_text(txt_path):
    """Extrai valores do arquivo de ground truth e normaliza."""
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    
    transcriptions = [line.split(",")[-1].strip() for line in lines if "," in line]
    return set(clean_text(t, preserve_accents=True) for t in transcriptions)

def check_field_accuracy(organized_info, ground_truth_text):
    """Verifica se os campos extraídos correspondem ao ground truth com uma similaridade flexível."""
    results = {}
    total_fields = 0
    matched_fields = 0
    similarity_threshold = 0.75  # Mais flexível

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
    # Define diretórios
    data_dirs = {"CNH_Aberta": "data/CNH_Aberta", "RG_Aberto": "data/RG_Aberto"}
    results_dir = "results"
    summary = {"CNH_Aberta": [], "RG_Aberto": []}

    total_files = 0
    processed_files = 0
    failed_files = []  # Lista de arquivos com erro
    accuracy_sums = {"CNH_Aberta": 0, "RG_Aberto": 0}  # Soma das acurácias por tipo de documento
    document_stats = {"CNH_Aberta": {"total": 0, "processed": 0}, "RG_Aberto": {"total": 0, "processed": 0}}

    for sub_dir, data_path in data_dirs.items():
        results_path = os.path.join(results_dir, sub_dir)
        
        if not os.path.exists(results_path):
            print(f"❌ Diretório não encontrado: {results_path}. Pulando.")
            continue

        print(f"🔍 Processando diretório: {results_path}")
        
        for file_name in os.listdir(results_path):
            if file_name.endswith(".json"):
                total_files += 1
                document_stats[sub_dir]["total"] += 1
                json_output_file = os.path.join(results_path, file_name)
                base_name = file_name.replace(".json", "")
                txt_file = os.path.join(data_path, f"{base_name}_gt_ocr.txt")

                if not os.path.exists(txt_file):
                    print(f"⚠️ Ground truth ausente para {file_name}. Arquivo será incluído no relatório com erro.")
                    failed_files.append({"file_name": file_name, "error": "Ground truth ausente"})
                    continue

                try:
                    # Carrega JSON extraído
                    with open(json_output_file, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                        extracted_info = json_data.get("informacoes organizadas", {})

                    if not extracted_info:
                        print(f"⚠️ JSON {file_name} está vazio ou não tem campos esperados. Incluindo no relatório.")
                        failed_files.append({"file_name": file_name, "error": "JSON sem informações organizadas"})
                        continue

                    # Extrai texto do ground truth
                    ground_truth_text = extract_ground_truth_text(txt_file)

                    # Calcula acurácia
                    field_results, overall_accuracy = check_field_accuracy(extracted_info, ground_truth_text)

                    # Atualiza JSON com os resultados
                    json_data["overall_accuracy"] = overall_accuracy
                    json_data["field_results"] = field_results

                    # Salva JSON atualizado
                    with open(json_output_file, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)

                    print(f"✅ {file_name} atualizado com acurácia: {overall_accuracy:.2%}")
                    summary[sub_dir].append({"file_name": file_name, "accuracy": overall_accuracy})
                    accuracy_sums[sub_dir] += overall_accuracy
                    processed_files += 1
                    document_stats[sub_dir]["processed"] += 1
                
                except Exception as e:
                    print(f"❌ Erro ao calcular acurácia para {file_name}: {e}")
                    failed_files.append({"file_name": file_name, "error": str(e)})

    # Calcula média de acurácia e percentual de processamento por tipo de documento
    average_accuracies = {
        "CNH_Aberta": (accuracy_sums["CNH_Aberta"] / len(summary["CNH_Aberta"])) if summary["CNH_Aberta"] else 0,
        "RG_Aberto": (accuracy_sums["RG_Aberto"] / len(summary["RG_Aberto"])) if summary["RG_Aberto"] else 0
    }
    processed_percentages = {
        doc_type: (stats["processed"] / stats["total"]) * 100 if stats["total"] > 0 else 0
        for doc_type, stats in document_stats.items()
    }

    # Salva resumo final
    summary_file = os.path.join(results_dir, "summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({
            "average_accuracy": sum(accuracy_sums.values()) / processed_files if processed_files > 0 else 0,
            "processed_percentage": (processed_files / total_files) * 100 if total_files > 0 else 0,
            "total_files": total_files,
            "processed_files": processed_files,
            "failed_files": failed_files,
            "document_results": summary,
            "CNH_average_accuracy": average_accuracies["CNH_Aberta"],
            "RG_average_accuracy": average_accuracies["RG_Aberto"],
            "CNH_processed_percentage": processed_percentages["CNH_Aberta"],
            "RG_processed_percentage": processed_percentages["RG_Aberto"]
        }, f, ensure_ascii=False, indent=4)

    print(f"📊 Resumo salvo em {summary_file}")
