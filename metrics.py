import os
import json

def check_field_accuracy(organized_info, extracted_info):
    """Check if fields from organized information are exactly present in the extracted information."""
    results = {}
    total_fields = 0
    matched_fields = 0

    for key, value in organized_info.items():
        if isinstance(value, list):
            # For list fields like Filiacao
            sub_results = []
            for item in value:
                total_fields += 1
                matched = item in extracted_info.get(key, [])
                sub_results.append({"value": item, "matched": matched})
                if matched:
                    matched_fields += 1
            results[key] = sub_results
        else:
            # For single fields
            total_fields += 1
            matched = value == extracted_info.get(key, "")
            results[key] = {"value": value, "matched": matched}
            if matched:
                matched_fields += 1

    accuracy = matched_fields / total_fields if total_fields > 0 else 0
    return results, accuracy

if __name__ == "__main__":
    # Define path
    json_output_file = "results/output.json"  # Path to the JSON output file with extracted data

    # Ensure the path exists
    if os.path.exists(json_output_file):
        try:
            # Load the extracted information from the JSON output file
            with open(json_output_file, "r", encoding="utf-8") as f:
                json_data = json.load(f)
                extracted_info = json_data.get("Informações Organizadas", {})
                ground_truth = json_data.get("Informações Organizadas", {})  # Use the same data as ground truth

            # Check field accuracy
            field_results, overall_accuracy = check_field_accuracy(ground_truth, extracted_info)

            # Display the results
            result = {
                "overall_accuracy": overall_accuracy,
                "field_results": field_results
            }
            print(json.dumps(result, indent=4, ensure_ascii=False))

        except Exception as e:
            print(f"Erro ao calcular a acurácia: {e}")
    else:
        print("JSON output file not found. Please check the path.")