// Seleciona todos os card-headers
const cardHeaders = document.querySelectorAll('.card-header');

// Adiciona um evento de clique a cada cabeçalho
cardHeaders.forEach(header => {
    header.addEventListener('click', () => {
        // Seleciona o conteúdo do dropdown (próximo elemento após o header)
        const content = header.nextElementSibling;
        // Seleciona o ícone dentro do header
        let icon = document.querySelectorAll('.icon_plus');

        // Alterna a classe 'open' no conteúdo para mostrar/esconder
        content.classList.toggle('open');
        // Alterna a classe 'active' no header para estilizar o ícone
        header.classList.toggle('active');

        // Alterna o ícone entre "plus" e "minus"
        if (header.classList.contains('active')) {
            icon.src = "{% static 'icons/minus.svg' %}"; // Troca para o ícone de "minus"
            icon.alt = "icon-minus";
        } else {
            icon.src = "{% static 'icons/plus.svg' %}"; // Volta para o ícone de "plus"
            icon.alt = "icon-plus";
        }
    });
});