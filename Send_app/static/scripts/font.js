// Seleciona os botões
const increaseBtn = document.querySelector('.increaseFont');
const resetBtn = document.querySelector('.resetFont');
const decreaseBtn = document.querySelector('.decreaseFont');

// Define o tamanho inicial da fonte (em pixels)
let fontSize = 16; // Tamanho padrão
const defaultFontSize = 16; // Tamanho para reset
const step = 2; // Incremento/decremento em pixels

// Função para atualizar o tamanho da fonte
function updateFontSize() {
    document.body.style.fontSize = `${fontSize}px`;
}

// Evento para aumentar a fonte
increaseBtn.addEventListener('click', (e) => {
    e.preventDefault(); // Evita comportamento padrão do link
    fontSize += step;
    updateFontSize();
});

// Evento para diminuir a fonte
decreaseBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fontSize = Math.max(10, fontSize - step); // Evita fontes muito pequenas
    updateFontSize();
});

// Evento para redefinir a fonte
resetBtn.addEventListener('click', (e) => {
    e.preventDefault();
    fontSize = defaultFontSize;
    updateFontSize();
});