import abstra.forms as af
from abstra.tasks import send_task
import json
from vision_api_project.process_document import process_document
import tempfile

# Allow the user to specify the document type before uploading a file
document_type = af.read_dropdown("Selecione o tipo de documento:", options=["RG", "CPF", "CNH"])
uploaded_file = af.read_file("Faça o upload do documento para processar:")

if uploaded_file:
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.file.read()) 
            temp_file_path = temp_file.name 

        resultado = process_document(temp_file_path, document_type)

        af.display_html("<h3>Resultado do processamento:</h3>")
        af.display_html("<pre>{}</pre>".format(json.dumps(resultado, indent=4, ensure_ascii=False)))

    except Exception as e:
        af.display_html(f"<span style='color: red;'>Ocorreu um erro: {e}. Por favor, tente novamente ou contate o suporte.</span>")
else:
    af.display_html("<span style='color: orange;'>Nenhum arquivo enviado. Por favor, faça o upload para continuar.</span>")


