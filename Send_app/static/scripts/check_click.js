document.addEventListener('DOMContentLoaded', function () {
    const checkSim = document.getElementById('check_sim');
    const checkNao = document.getElementById('check_nao');
    const uploadContainer = document.getElementById('upload-container');

    // Adiciona evento ao checkbox "Sim"
    checkSim.addEventListener('change', function () {
        if (checkSim.checked) {
            uploadContainer.style.display = 'block'; // Mostra o campo de upload
        }
    });

    // Adiciona evento ao checkbox "Não"
    checkNao.addEventListener('change', function () {
        if (checkNao.checked) {
            uploadContainer.style.display = 'none'; // Oculta o campo de upload
        }
    });
});