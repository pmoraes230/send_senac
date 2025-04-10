function formatarData() {
    const diasSemana = [
        'Domingo', 
        'Segunda', 
        'Terça', 
        'Quarta', 
        'Quinta', 
        'Sexta', 
        'Sábado'
    ];
    
    const meses = [
        'janeiro', 
        'fevereiro', 
        'março', 
        'abril', 
        'maio', 
        'junho', 
        'julho', 
        'agosto', 
        'setembro', 
        'outubro', 
        'novembro', 
        'dezembro'
    ];
    
    const data = new Date();
    const diaSemana = diasSemana[data.getDay()];
    const dia = String(data.getDate()).padStart(2, '0'); // Adiciona 0 à esquerda se necessário
    const mes = meses[data.getMonth()];
    const ano = data.getFullYear();
    
    return `${diaSemana}, ${dia} de ${mes} de ${ano}`;
}

// Para usar no HTML:
document.getElementById('date').textContent = formatarData();