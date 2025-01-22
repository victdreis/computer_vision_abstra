import abstra.forms as af
from abstra.tasks import send_task
import json
from vision_api_project.process_document import process_document
import tempfile

# Dropdown to select document type
document_type = af.read_dropdown(
    "Selecione o tipo de documento:", 
    options=[
        "RG",
        "CPF",
        "CNH",
        "Certidão de Nascimento",
        "Certidão de Casamento",
        "Comprovante de Endereço",
        "CTPS",
        "Holerite",
        "Imposto de Renda",
        "Extrato do FGTS"
    ]
)

# File upload by user
uploaded_file = af.read_file("Faça o upload do documento para processar:")

if uploaded_file:
    try:
        # Save file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.file.read()) 
            temp_file_path = temp_file.name 

        # Process the document
        result = process_document(temp_file_path, document_type)

        # Display the result in a formatted way
        if isinstance(result, dict) and "Texto Visível" in result:
            # Display visible text
            af.display_html(result["Texto Visível"])
        else:
            # Display formatted JSON
            af.display_html("<pre>{}</pre>".format(json.dumps(result, indent=4, ensure_ascii=False)))

    except Exception as e:
        # Display error message
        af.display_html(f"<span style='color: red;'>Ocorreu um erro: {e}. Por favor, tente novamente ou contate o suporte.</span>")
else:
    # Message when no file is uploaded
    af.display_html("<span style='color: orange;'>Nenhum arquivo enviado. Por favor, faça o upload para continuar.</span>")
