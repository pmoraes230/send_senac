const checkInputs = document.querySelectorAll('input[type="checkbox"]'); // Seleciona todos os checkboxes

checkInputs.forEach(checkbox => {
    checkbox.addEventListener('click', function () {
        checkInputs.forEach(otherCheckbox => {
            if (otherCheckbox !== checkbox) {
                otherCheckbox.checked = false; // Desmarca os outros checkboxes
            }
        });
    });
});