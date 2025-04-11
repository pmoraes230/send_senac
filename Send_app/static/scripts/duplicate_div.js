document.addEventListener('DOMContentLoaded', function() {
    // Função para adicionar mais campos
    document.getElementById('add-more').addEventListener('click', function (event) {
        event.preventDefault();

        const container = document.getElementById('dynamic-container');
        const categoriaDiv = container.children[0].cloneNode(true);
        const subcategoriaDiv = container.children[1].cloneNode(true);

        const timestamp = Date.now();
        const newCategoriaId = `id_categoria_${timestamp}`;
        const newSubcategoriaId = `id_subcategoria_${timestamp}`;

        const categoriaSelect = categoriaDiv.querySelector('select');
        const subcategoriaSelect = subcategoriaDiv.querySelector('select');
        categoriaSelect.id = newCategoriaId;
        categoriaSelect.name = `id_categoria_${timestamp}`;
        categoriaDiv.querySelector('label').setAttribute('for', newCategoriaId);
        subcategoriaSelect.id = newSubcategoriaId;
        subcategoriaSelect.name = `id_subcategoria_${timestamp}`;
        subcategoriaDiv.querySelector('label').setAttribute('for', newSubcategoriaId);

        categoriaSelect.value = '';
        subcategoriaSelect.innerHTML = '<option value="" disabled selected>Selecione uma subcategoria</option>';

        container.appendChild(categoriaDiv);
        container.appendChild(subcategoriaDiv);

        if (typeof jQuery !== 'undefined' && jQuery.fn.select2) {
            jQuery(categoriaSelect).select2('destroy').select2();
            jQuery(subcategoriaSelect).select2('destroy').select2();
        }

        // Reaplica lógica de subcategorias
        categoriaSelect.addEventListener('change', function () {
            const url = categoriaSelect.getAttribute('data-subcategories-url');
            if (url) {
                fetch(`${url}?category_id=${this.value}`)
                    .then(response => response.json())
                    .then(data => {
                        subcategoriaSelect.innerHTML = '<option value="" disabled selected>Selecione uma subcategoria</option>';
                        data.forEach(sub => {
                            const option = document.createElement('option');
                            option.value = sub.id;
                            option.textContent = sub.nome;
                            subcategoriaSelect.appendChild(option);
                        });
                        if (typeof jQuery !== 'undefined' && jQuery.fn.select2) {
                            jQuery(subcategoriaSelect).select2('destroy').select2();
                        }
                    })
                    .catch(error => console.error('Erro ao carregar subcategorias:', error));
            }
        });
    });

    // Função para remover campos
    document.getElementById('remove-column').addEventListener('click', function (event) {
        event.preventDefault();
        const container = document.getElementById('dynamic-container');
        const children = container.children;
        if (children.length > 2) {
            container.removeChild(children[children.length - 1]);
            container.removeChild(children[children.length - 1]);
        }
    });

    // Validação do formulário
    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        const selects = form.querySelectorAll('select[name^="id_usuario"], select[name^="id_setor"], select[name^="id_categoria"], select[name^="id_subcategoria"]');
        let hasError = false;

        selects.forEach(select => {
            if (!select.value || select.value === '' || isNaN(select.value)) {
                hasError = true;
                select.classList.add('error');
                const label = select.closest('.form-group').querySelector('label');
                alert(`Por favor, selecione um valor válido para ${label.textContent}`);
            } else {
                select.classList.remove('error');
            }
        });

        if (hasError) {
            event.preventDefault();
        }
    });
});