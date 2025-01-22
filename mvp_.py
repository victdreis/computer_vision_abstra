import abstra.forms as af
from abstra.tasks import send_task
import json
from vision_api_project.process_document import process_document
import tempfile

# Dropdown para selecionar o tipo de documento
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

# Upload do arquivo pelo usuário
uploaded_file = af.read_file("Faça o upload do documento para processar:")

if uploaded_file:
    try:
        # Salvar arquivo temporariamente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
            temp_file.write(uploaded_file.file.read()) 
            temp_file_path = temp_file.name 

        # Processar o documento
        resultado = process_document(temp_file_path, document_type)

        # Exibir o resultado de forma formatada
        if isinstance(resultado, dict) and "Texto Visível" in resultado:
            # Exibir texto visível
            af.display_html(resultado["Texto Visível"])
        else:
            # Exibir JSON formatado
            af.display_html("<pre>{}</pre>".format(json.dumps(resultado, indent=4, ensure_ascii=False)))

    except Exception as e:
        # Exibir erro caso ocorra durante o processamento
        af.display_html(f"<span style='color: red;'>Ocorreu um erro: {e}. Por favor, tente novamente ou contate o suporte.</span>")
else:
    # Mensagem para o caso de nenhum arquivo ser enviado
    af.display_html("<span style='color: orange;'>Nenhum arquivo enviado. Por favor, faça o upload para continuar.</span>")
