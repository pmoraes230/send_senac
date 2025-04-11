const input = document.querySelector('#form-upload-031578');
const progressBar = document.querySelector('.progress-bar');
const messageDiv = document.querySelector('#message');
const previewContainer = document.createElement('div');
previewContainer.id = 'image-preview';
previewContainer.style.display = 'flex';
previewContainer.style.flexWrap = 'wrap';
previewContainer.style.marginBottom = '10px';
messageDiv.parentNode.insertBefore(previewContainer, messageDiv);

const maxSize = 35 * 1024 * 1024;
const allowedFormats = ['jpg', 'jpeg', 'png', 'pdf', 'xls', 'xlsx', 'doc', 'docx', 'txt', 'eml', 'zip'];
const imageFormats = ['jpg', 'jpeg', 'png'];

function clearPreview() {
    previewContainer.innerHTML = '';
}

function addImagePreview(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
        const img = document.createElement('img');
        img.src = e.target.result;
        img.style.maxWidth = '100px';
        img.style.maxHeight = '100px';
        img.style.margin = '5px';
        img.style.border = '1px solid #ccc';
        img.alt = file.name;
        previewContainer.appendChild(img);
    };
    reader.onerror = function () {
        console.error(`Erro ao ler o arquivo ${file.name}`);
        messageDiv.className = 'error';
        messageDiv.textContent = `Erro ao carregar a pré-visualização de ${file.name}.`;
    };
    reader.readAsDataURL(file);
}

if (input) {
    input.addEventListener('change', async () => {
        console.log('Input de arquivos acionado:', input.files.length, 'arquivos selecionados.');
        const files = input.files;
        let totalSize = 0;

        progressBar.style.width = '0%';
        messageDiv.textContent = '';
        clearPreview();

        if (files.length === 0) {
            messageDiv.className = 'info';
            messageDiv.textContent = 'Nenhum arquivo selecionado.';
            return;
        }

        for (let file of files) {
            totalSize += file.size;
            const fileExt = file.name.split('.').pop().toLowerCase();

            if (!allowedFormats.includes(fileExt)) {
                messageDiv.className = 'error';
                messageDiv.textContent = `Formato .${fileExt} não permitido. Formatos aceitos: ${allowedFormats.join(', ')}.`;
                input.value = '';
                clearPreview();
                return;
            }

            if (totalSize > maxSize) {
                messageDiv.className = 'error';
                messageDiv.textContent = 'O tamanho total dos arquivos excede 35MB.';
                input.value = '';
                clearPreview();
                return;
            }

            if (imageFormats.includes(fileExt)) {
                addImagePreview(file);
            }
        }
    });
} else {
    console.error('Input de upload não encontrado (#form-upload-031578).');
}

const fileInputButton = document.querySelector('.fileinput-button');
if (fileInputButton) {
    fileInputButton.addEventListener('click', (event) => {
        event.preventDefault();
        console.log('Botão de seleção de arquivos clicado.');
        input.click();
    });
}