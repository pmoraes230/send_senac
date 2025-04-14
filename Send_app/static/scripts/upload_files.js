document.querySelector('.fileinput-button').addEventListener('click', function () {
    const fileInput = this.querySelector('input[type="file"]');
    fileInput.click();
});

// Quando o usuário selecionar arquivos
document.querySelector('.fileupload').addEventListener('change', function (e) {
    const files = e.target.files;
    if (files.length > 0) {
        simulateUpload(files);
    }
});

function simulateUpload(files) {
    const progressBar = document.querySelector('.progress-bar');
    const messageDiv = document.querySelector('#message');
    const maxSize = 35 * 1024 * 1024; // 35MB em bytes

    // Validar o tamanho dos arquivos
    for (let i = 0; i < files.length; i++) {
        if (files[i].size > maxSize) {
            messageDiv.innerHTML = '<p class="text-danger">Arquivo excede o limite de 35MB.</p>';
            return;
        }
    }

    // Resetar a barra de progresso e mensagens
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    messageDiv.innerHTML = '';

    // Simular o progresso do upload
    let progress = 0;
    const interval = setInterval(() => {
        progress += 10; // Incrementa 10% a cada 200ms
        progressBar.style.width = progress + '%';
        progressBar.setAttribute('aria-valuenow', progress);

        if (progress >= 100) {
            clearInterval(interval);
            messageDiv.innerHTML = '<p class="text-success">Upload concluído com sucesso!</p>';
        }
    }, 200); // Ajuste o tempo (200ms) para controlar a velocidade da simulação
}