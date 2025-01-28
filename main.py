import json
import os
from vision_api_project.process_document import process_document

if __name__ == "__main__":
    # Define input and output directories
    input_dirs = ["data/CNH_Aberta", "data/RG_Aberto"]  # List of folders to process
    results_dir = "results"  # Path to save the JSON output files

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    # Process each directory
    for input_dir in input_dirs:
        print(f"Processing directory: {input_dir}")

        # Ensure results subdirectory exists for the current input directory
        sub_results_dir = os.path.join(results_dir, os.path.basename(input_dir))
        os.makedirs(sub_results_dir, exist_ok=True)

        # Process all files in the current input directory
        for file_name in os.listdir(input_dir):
            if file_name.endswith("_in.jpg"):
                base_name = file_name.replace("_in.jpg", "")
                image_path = os.path.join(input_dir, file_name)
                output_file = os.path.join(sub_results_dir, f"{base_name}.json")

                try:
                    # Processes the document and organizes the extracted data
                    result = process_document(image_path, "CNH" if "CNH" in input_dir else "RG")

                    # Displays the result in the terminal
                    print(json.dumps(result, indent=4, ensure_ascii=False))

                    # Saves the result to a JSON file
                    with open(output_file, "w", encoding="utf-8") as f:
                        json.dump(result, f, ensure_ascii=False, indent=4)

                    print(f"Processamento concluído para {file_name}! Resultado salvo em '{output_file}'.")
                except Exception as e:
                    print(f"Erro ao processar {file_name}: {e}")
