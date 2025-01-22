import json
from vision_api_project.process_document import process_document

if __name__ == "__main__":
    # Example image path
    image_path = "certidao_casamento2.jpeg"  # Replace with the actual path
    document_type = "Certidão de Casamento"  # Could be "RG", "CPF", "CNH", etc.

    try:
        # Process the document and organize data
        result = process_document(image_path, document_type)

        # Display the result
        print(json.dumps(result, indent=4, ensure_ascii=False))

        # Save the result to a JSON file
        with open("results/output.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        print("Processamento concluído! Resultado salvo em 'results/output.json'.")
    except Exception as e:
        print(f"Erro ao processar o documento: {e}")

