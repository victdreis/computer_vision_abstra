import json
import os
import logging
from vision_api_project.process_document import process_document, process_document_with_vote

# Configurar logs para depuração
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

if __name__ == "__main__":
    # Define input and output directories
    input_dirs = ["data/CNH_Aberta", "data/RG_Aberto"]
    results_dir = "results"

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    failed_files = []  # Stores files that failed processing

    for input_dir in input_dirs:
        logging.info(f"📂 Processing directory: {input_dir}")

        # Ensure a subdirectory exists in results for this category
        sub_results_dir = os.path.join(results_dir, os.path.basename(input_dir))
        os.makedirs(sub_results_dir, exist_ok=True)

        for file_name in os.listdir(input_dir):
            if not file_name.endswith("_in.jpg"):
                continue  # Skip non-image files

            base_name = file_name.replace("_in.jpg", "")
            image_path = os.path.join(input_dir, file_name)
            output_file = os.path.join(sub_results_dir, f"{base_name}.json")

            try:
                logging.info(f"🔎 Processing {file_name}...")

                # Process document
                result = process_document(image_path, "CNH" if "CNH" in input_dir else "RG")

                # Check if the result is empty or contains an error
                if not result or "Erro" in result or not any(result.get("Informações Organizadas", {}).values()):
                    logging.warning(f"⚠️ Processing failed for {file_name}. Retrying with vote(5)...")
                    result = process_document_with_vote(image_path, "CNH" if "CNH" in input_dir else "RG")

                    # If it still fails, add to failed files list
                    if not result or "Erro" in result or not any(result.get("Informações Organizadas", {}).values()):
                        logging.error(f"❌ Final processing attempt failed for {file_name}. Skipping.")
                        failed_files.append(file_name)
                        continue

                # Save the result
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=4)
                    f.flush()
                    os.fsync(f.fileno())

                logging.info(f"✅ Successfully processed {file_name}. Result saved at '{output_file}'.")

            except Exception as e:
                logging.error(f"❌ Error processing {file_name}: {e}")
                failed_files.append(file_name)

    # Show failed files summary
    if failed_files:
        logging.warning("\n⚠️ The following files failed to process:")
        for file in failed_files:
            logging.warning(f"   ❌ {file}")
