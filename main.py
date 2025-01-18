import json
from vision_api_project.process_document import process_document

if __name__ == "__main__":
    # Caminho da imagem de exemplo
    image_path = "data/00018415_in.jpg"  # Substitua pelo caminho real
    document_type = "RG"  # Pode ser "RG", "CPF", "CNH", etc.

    try:
        # Processar o documento e organizar os dados
        resultado = process_document(image_path, document_type)

        # Exibir resultado
        print(json.dumps(resultado, indent=4, ensure_ascii=False))

        # Salvar em um arquivo JSON
        with open("results/output.json", "w", encoding="utf-8") as f:
            json.dump(resultado, f, ensure_ascii=False, indent=4)

        print("Processamento concluído! Resultado salvo em 'results/output.json'.")

    except Exception as e:
        print(f"Erro ao processar o documento: {e}")
