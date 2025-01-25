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
        "FGTS"
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

        # Prepare the content to display
        display_content = "<h3>Resultado:</h3>"

        # Display "Texto Visível" if available
        display_content += "<h3>Texto Visível:</h3>"
        display_content += f"<p>{result.get('Texto Visível', 'Texto visível não disponível.')}</p>"

        # Display the organized result as JSON
        display_content += "<h3>Resultado Organizado:</h3>"
        display_content += f"<pre>{json.dumps(result.get('Informações Organizadas', {}), indent=4, ensure_ascii=False)}</pre>"

        # Display the final content
        af.display_html(display_content)

    except Exception as e:
        # Display error message
        af.display_html(f"<span style='color: red;'>Ocorreu um erro: {e}. Por favor, tente novamente ou contate o suporte.</span>")
else:
    # Message when no file is uploaded
    af.display_html("<span style='color: orange;'>Nenhum arquivo enviado. Por favor, faça o upload para continuar.</span>")
