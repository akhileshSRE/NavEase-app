function confirmDelete(key) {
    if (confirm("Do you want to delete " + key + "?")) {
        fetch('/api/v1/delete', {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: key })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                window.location.reload();
            } else {
                alert(data.error);
            }
        });
    }
}

function updateValue(key, value) {
    const newValue = prompt("Update value for " + key, value);
    if (newValue !== null) {
        fetch('/api/v1/update', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ key: key, value: newValue })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                alert(data.message);
                window.location.reload();
            } else {
                alert(data.error);
            }
        });
    }
}

// Function to remove flash messages after they fade out
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        const flashes = document.querySelectorAll('.flash-message');
        flashes.forEach(flash => {
            flash.style.display = 'none';
        });
    }, 5000); // Match the duration of the fadeOut animation
});

function filterTable() {
    const searchInput = document.getElementById("search-input");
    const filter = searchInput.value.toLowerCase();
    const table = document.querySelector(".dashboard-table");
    const rows = table.getElementsByTagName("tr");

    for (let i = 1; i < rows.length; i++) {
        const cells = rows[i].getElementsByTagName("td");
        let shouldDisplay = false;

        for (let j = 0; j < cells.length; j++) {
            const cellValue = cells[j].textContent.toLowerCase();
            if (cellValue.includes(filter)) {
                shouldDisplay = true;
                break;
            }
        }

        rows[i].style.display = shouldDisplay ? "" : "none";
    }
}

function toggleSidenav() {
    const sidenav = document.querySelector('.sidenav');
    const mainContent = document.querySelector('.main-content');
    const toggleBtn = document.querySelector('.toggle-btn');

    sidenav.classList.toggle('active');
    sidenav.classList.toggle('inactive');
    mainContent.classList.toggle('sidenav-active');
    toggleBtn.classList.toggle('active');
}