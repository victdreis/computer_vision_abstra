import json
from vision_api_project.process_document import processar_documento

if __name__ == "__main__":
    caminho_imagem = "data/BID Sample Dataset/CNH_Aberta/00000028_in.jpg"  # Substitua pelo caminho da sua imagem
    tipo_documento = "CNH"  # Substitua por "CPF", "RG" ou "CNH"

    resultado = processar_documento(caminho_imagem, tipo_documento)
    print(json.dumps(resultado, indent=4, ensure_ascii=False))

    # Salvando o resultado no arquivo
    with open("results/output.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=4)
