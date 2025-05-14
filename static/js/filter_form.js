document.addEventListener('DOMContentLoaded', function() {
    const filterForms = document.querySelectorAll('.form-filter-panel');

    filterForms.forEach(form => {
        const inputs = form.querySelectorAll('input[type="date"], select');
        const clearButtonLink = form.querySelector('#clear-filter-btn'); // Changed selector to ID
        
        if (!clearButtonLink) {
            console.warn('Clear filter button not found in a form-filter-panel.');
            return;
        }

        // Find the parent div of the clear button to hide/show
        let clearButtonContainer = clearButtonLink.closest('.col-md-1, .col-md-2');
        if (!clearButtonContainer) clearButtonContainer = clearButtonLink.parentElement; 
        
        if (!clearButtonContainer) {
            console.warn('Could not find container for clear filter button.');
            return;
        }

        function checkFilters() {
            let isAnyFilterActive = false;
            inputs.forEach(input => {
                if (input.tagName === 'SELECT') {
                    if (input.selectedIndex !== 0 && input.value !== '') {
                        isAnyFilterActive = true;
                    }
                } else if (input.type === 'date') {
                    if (input.value) {
                        isAnyFilterActive = true;
                    }
                }
            });

            if (isAnyFilterActive) {
                clearButtonContainer.style.display = 'flex'; // Assuming it's a flex item for alignment
            } else {
                clearButtonContainer.style.display = 'none';
            }
        }

        // Initial check
        checkFilters();

        // Check on input change
        inputs.forEach(input => {
            input.addEventListener('change', checkFilters);
        });
    });
}); 