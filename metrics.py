import os
import json
import unicodedata
from difflib import SequenceMatcher

def clean_text(text):
    """Normaliza o texto removendo acentos, espaços extras e deixando minúsculo."""
    if not text:
        return ""
    text = text.lower().strip()
    text = ''.join(c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c))  # Remove acentos
    text = " ".join(text.split())  # Remove espaços extras
    return text

def similar(a, b):
    """Verifica a similaridade entre dois textos usando SequenceMatcher."""
    return SequenceMatcher(None, a, b).ratio()

def extract_ground_truth_text(txt_path):
    """Extrai os valores da ground truth do TXT e normaliza."""
    with open(txt_path, "r", encoding="utf-8", errors="replace") as f:
        lines = f.readlines()
    
    transcriptions = [line.split(",")[-1].strip() for line in lines if "," in line]
    return set(clean_text(t) for t in transcriptions)  # Normaliza para comparação

def check_field_accuracy(organized_info, ground_truth_text):
    """Verifica se os campos extraídos batem com os do TXT usando similaridade."""
    results = {}
    total_fields = 0
    matched_fields = 0
    similarity_threshold = 0.85  # Reduz o threshold para maior flexibilidade

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
    # Define diretórios
    data_dirs = {"CNH_Aberta": "data/CNH_Aberta", "RG_Aberto": "data/RG_Aberto"}
    results_dir = "results"
    summary = []

    for sub_dir, data_path in data_dirs.items():
        results_path = os.path.join(results_dir, sub_dir)

        if not os.path.exists(results_path):
            print(f"❌ Diretório não encontrado: {results_path}. Pulando.")
            continue

        print(f"🔍 Processando diretório: {results_path}")

        for file_name in os.listdir(results_path):
            if file_name.endswith(".json"):
                json_output_file = os.path.join(results_path, file_name)
                base_name = file_name.replace(".json", "")
                txt_file = os.path.join(data_path, f"{base_name}_gt_ocr.txt")

                if not os.path.exists(txt_file):
                    print(f"⚠️ Arquivo ground truth não encontrado para {file_name}. Pulando.")
                    continue

                try:
                    # Carrega o JSON extraído
                    with open(json_output_file, "r", encoding="utf-8") as f:
                        json_data = json.load(f)
                        extracted_info = json_data.get("Informações Organizadas", {})

                    if not extracted_info:
                        print(f"⚠️ JSON {file_name} está vazio. Pulando.")
                        continue

                    # Extrai texto do ground truth
                    ground_truth_text = extract_ground_truth_text(txt_file)

                    # Calcula a acurácia
                    field_results, overall_accuracy = check_field_accuracy(extracted_info, ground_truth_text)

                    # Atualiza JSON com os resultados
                    json_data["overall_accuracy"] = overall_accuracy
                    json_data["field_results"] = field_results

                    # Salva o JSON atualizado
                    with open(json_output_file, "w", encoding="utf-8") as f:
                        json.dump(json_data, f, ensure_ascii=False, indent=4)

                    print(f"✅ Atualizado {file_name} com acurácia: {overall_accuracy:.2%}")
                    summary.append({"file_name": file_name, "accuracy": overall_accuracy})

                except Exception as e:
                    print(f"❌ Erro ao calcular a acurácia para {file_name}: {e}")

    # Salva o resumo final
    summary_file = os.path.join(results_dir, "summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump({"average_accuracy": sum(x["accuracy"] for x in summary) / len(summary) if summary else 0, "document_results": summary}, f, ensure_ascii=False, indent=4)
    print(f"📊 Resumo salvo em {summary_file}")
