document.addEventListener('DOMContentLoaded', function () {
    const table = document.getElementById('cv-table');
    if (!table) return;

    const tbody = table.querySelector('tbody');
    const sortSelect = document.getElementById('sort-by');

    function sortTable() {
        const sortValue = sortSelect.value;
        const rows = Array.from(tbody.querySelectorAll('tr'));

        rows.sort((a, b) => {
            const scoreA = parseFloat(a.dataset.score) || 0;
            const scoreB = parseFloat(b.dataset.score) || 0;
            const dateA = a.dataset.date || '';
            const dateB = b.dataset.date || '';

            if (sortValue === 'score_desc') return scoreB - scoreA;
            if (sortValue === 'score_asc') return scoreA - scoreB;
            if (sortValue === 'date_desc') return dateB.localeCompare(dateA);
            return 0;
        });

        rows.forEach(row => tbody.appendChild(row));
    }

    sortSelect.addEventListener('change', sortTable);

    // sort mặc định khi mở modal
    sortTable();
});