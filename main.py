import json
import os
import logging
from src.process_document import process_document
from src.decorators import vote, has_valid_data

# Configure logging for debugging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def process_document_with_vote(image_path, document_type):
    """Process a document using the voting mechanism if the first attempt fails."""
    logging.warning(f"⚠️ Retrying {image_path} with vote(5)...")
    voted_process = vote(5)(process_document)
    return voted_process(image_path, document_type)

if __name__ == "__main__":
    # Define input and output directories
    input_dirs = ["data/CNH_Aberta", "data/RG_Aberto"]
    results_dir = "results"

    # Ensure results directory exists
    os.makedirs(results_dir, exist_ok=True)

    failed_files = []

    for input_dir in input_dirs:
        logging.info(f"📂 Processing directory: {input_dir}")

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

                # Determine document type based on folder name
                document_type = (
                    "CNH" if "CNH" in input_dir else
                    "RG" if "RG" in input_dir else
                    "Certidão de Casamento" if "Casamento" in input_dir else
                    "Holerite" if "Holerite" in input_dir else
                    "FGTS" if "FGTS" in input_dir else
                    "Documento Desconhecido"
                )

                # Process document
                result = process_document(image_path, document_type)

                # Check if the result is valid
                if not has_valid_data(result.get("Informações Organizadas", {})):
                    logging.warning(f"⚠️ Processing failed for {file_name}. Retrying with vote(5)...")
                    result = process_document_with_vote(image_path, document_type)

                    if not has_valid_data(result.get("Informações Organizadas", {})):
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
