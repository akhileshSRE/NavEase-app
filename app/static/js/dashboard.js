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
    const input = document.getElementById('search-input').value.toUpperCase();
    const tables = document.querySelectorAll('.dashboard-table tbody');
    tables.forEach(table => {
        const rows = table.getElementsByTagName('tr');
        Array.from(rows).forEach(row => {
            const cells = row.getElementsByTagName('td');
            if (cells[0].innerText.toUpperCase().indexOf(input) > -1) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });
}

function toggleSidenav() {
    const sidenav = document.querySelector('.sidenav');
    const mainContent = document.querySelector('.main-content');
    const toggleBtn = document.querySelector('.toggle-btn');

    sidenav.classList.toggle('active');
    mainContent.classList.toggle('sidenav-active');
    toggleBtn.classList.toggle('active');
}

function toggleAddForm() {
    const addForm = document.getElementById('add-form');
    addForm.style.display = addForm.style.display === 'none' ? 'block' : 'none';
}

function addKeyValue(event) {
    event.preventDefault();

    const key = document.getElementById('key').value;
    const value = document.getElementById('value').value;
    const level = document.getElementById('level').value;
    const submitButton = document.getElementById('add-key-value-btn');
    const buttonText = submitButton.querySelector('.button-text');
    const loadingSpinner = submitButton.querySelector('.loading-spinner');

    // Show loading state
    buttonText.style.display = 'none';
    loadingSpinner.style.display = 'inline-block';
    submitButton.disabled = true;

    fetch('/api/v1/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: key, value: value, level: level })
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        window.location.reload(); // Reload the page to show the new entry
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.error || 'An error occurred while adding the key-value pair');
    })
    .finally(() => {
        // Reset button state
        buttonText.style.display = 'inline-block';
        loadingSpinner.style.display = 'none';
        submitButton.disabled = false;
    });
}