import json
from vision_api_project.process_document import process_document

if __name__ == "__main__":
    # Example: path to the image and document type
    image_path = "ctps3.jpg"  # Replace with the path to your image
    document_type = "CTPS"  # Document type: RG, CPF, Certidão de Casamento, etc.

    try:
        # Processes the document and organizes the extracted data
        result = process_document(image_path, document_type)

        # Displays the result in the terminal
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # Saves the result to a JSON file
        with open("results/output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print("Processamento concluído! Resultado salvo em 'results/output.json'.")  # User-facing message in Portuguese
    except Exception as e:
        print(f"Erro ao processar o documento: {e}")  # User-facing error message in Portuguese

