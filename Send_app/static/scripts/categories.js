document.addEventListener('DOMContentLoaded', function() {
    const categoriaSelect = document.getElementById('id_categoria');
    const subcategoriaSelect = document.getElementById('id_subcategoria');
    const subcategoriesUrl = categoriaSelect.dataset.subcategoriesUrl; // Pega a URL do atributo data

    categoriaSelect.addEventListener('change', function() {
        const categoryId = this.value;
        
        if (categoryId) {
            fetch(subcategoriesUrl + "?category_id=" + categoryId)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
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
                .catch(error => {
                    console.error('Erro ao carregar subcategorias:', error);
                });
        } else {
            subcategoriaSelect.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.text = 'Selecione uma subcategoria';
            subcategoriaSelect.appendChild(defaultOption);
        }
    });
});