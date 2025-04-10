document.addEventListener('DOMContentLoaded', function() {
    let contador = 1;

    // Função para inicializar o evento de mudança em um select de categoria
    function inicializarCategoriaSelect(categoriaSelect, subcategoriaSelect) {
        const subcategoriesUrl = categoriaSelect.dataset.subcategoriesUrl;

        categoriaSelect.addEventListener('change', function() {
            const categoryId = this.value;
            
            if (categoryId) {
                fetch(subcategoriesUrl + "?category_id=" + categoryId)
                    .then(response => {
                        if (!response.ok) throw new Error('Network response was not ok');
                        return response.json();
                    })
                    .then(data => {
                        subcategoriaSelect.innerHTML = '';
                        const defaultOption = document.createElement('option');
                        defaultOption.value = '';
                        defaultOption.text = 'Selecione uma subcategoria';
                        subcategoriaSelect.appendChild(defaultOption);

                        data.forEach(subcategory => {
                            const option = document.createElement('option');
                            option.value = subcategory.id;
                            option.text = subcategory.nome;
                            subcategoriaSelect.appendChild(option);
                        });
                    })
                    .catch(error => console.error('Erro ao carregar subcategorias:', error));
            } else {
                subcategoriaSelect.innerHTML = '';
                const defaultOption = document.createElement('option');
                defaultOption.value = '';
                defaultOption.text = 'Selecione uma subcategoria';
                subcategoriaSelect.appendChild(defaultOption);
            }
        });
    }

    // Inicializa o primeiro par de selects
    const primeiroCategoria = document.getElementById('id_categoria_1');
    const primeiroSubcategoria = document.getElementById('id_subcategoria_1');
    inicializarCategoriaSelect(primeiroCategoria, primeiroSubcategoria);

    // Evento do botão de adicionar campos
    document.getElementById('adicionar-campos').addEventListener('click', function() {
        contador++;
        
        // Clona o primeiro grupo de campos
        const novoGrupo = document.querySelector('.campo-grupo').cloneNode(true);
        novoGrupo.id = `campo-grupo-${contador}`;
        
        // Atualiza os IDs e names dos novos selects
        const novaCategoria = novoGrupo.querySelector('select[name^="id_categoria"]');
        const novaSubcategoria = novoGrupo.querySelector('select[name^="id_subcategoria"]');
        
        novaCategoria.id = `id_categoria_${contador}`;
        novaCategoria.name = `id_categoria_${contador}`;
        novaCategoria.value = '';
        
        novaSubcategoria.id = `id_subcategoria_${contador}`;
        novaSubcategoria.name = `id_subcategoria_${contador}`;
        novaSubcategoria.innerHTML = '<option value="">Selecione uma subcategoria</option>';

        // Adiciona o novo grupo ao container
        document.getElementById('campos-container').appendChild(novoGrupo);

        // Inicializa a funcionalidade de filtragem para o novo par
        inicializarCategoriaSelect(novaCategoria, novaSubcategoria);
    });
});