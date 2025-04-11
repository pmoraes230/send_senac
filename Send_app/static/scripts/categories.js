document.addEventListener('DOMContentLoaded', function() {
    const categoriaSelect = document.getElementById('id_categoria');
    const subcategoriaSelect = document.getElementById('id_subcategoria');
    const subcategoriesUrl = categoriaSelect.dataset.subcategoriesUrl;

    function updateSubcategories(categoryId, targetSelect) {
        if (categoryId && categoryId !== '') {
            fetch(subcategoriesUrl + "?category_id=" + categoryId)
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    targetSelect.innerHTML = '';
                    const defaultOption = document.createElement('option');
                    defaultOption.value = '';
                    defaultOption.text = 'Selecione uma subcategoria';
                    defaultOption.disabled = true;
                    defaultOption.selected = true;
                    targetSelect.appendChild(defaultOption);

                    data.forEach(subcategory => {
                        const option = document.createElement('option');
                        option.value = subcategory.id;
                        option.text = subcategory.nome;
                        targetSelect.appendChild(option);
                    });

                    // Reaplica Select2, se presente
                    if (typeof jQuery !== 'undefined' && jQuery.fn.select2) {
                        jQuery(targetSelect).select2('destroy').select2();
                    }
                })
                .catch(error => {
                    console.error('Erro ao carregar subcategorias:', error);
                });
        } else {
            targetSelect.innerHTML = '';
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.text = 'Selecione uma subcategoria';
            defaultOption.disabled = true;
            defaultOption.selected = true;
            targetSelect.appendChild(defaultOption);
        }
    }

    categoriaSelect.addEventListener('change', function() {
        updateSubcategories(this.value, subcategoriaSelect);
    });
});