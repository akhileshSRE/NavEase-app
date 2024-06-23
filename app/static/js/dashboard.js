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
    setupOutsideClickListener();
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
    if (addForm.style.display === 'none' || addForm.style.display === '') {
        addForm.style.display = 'block';
    } else {
        addForm.style.display = 'none';
        resetForm();
    }
}

function setupOutsideClickListener() {
    const addForm = document.getElementById('add-form');
    const addIconContainer = document.querySelector('.add-icon-container');

    document.addEventListener('click', function(event) {
        const isClickInsideForm = addForm.contains(event.target);
        const isClickOnAddIcon = addIconContainer.contains(event.target);

        if (!isClickInsideForm && !isClickOnAddIcon && addForm.style.display === 'block') {
            toggleAddForm();
        }
    });
}

function addKeyValue(event) {
    event.preventDefault();

    const key = document.getElementById('key').value;
    const value = document.getElementById('value').value;
    const level = document.getElementById('level').value;
    const organization = document.getElementById('organization').value;
    const teams = Array.from(document.getElementById('teams').selectedOptions).map(option => option.value);
    const submitButton = document.getElementById('add-key-value-btn');
    const buttonText = submitButton.querySelector('.button-text');
    const loadingSpinner = submitButton.querySelector('.loading-spinner');

    // Show loading state
    buttonText.style.display = 'none';
    loadingSpinner.style.display = 'inline-block';
    submitButton.disabled = true;

    const data = { key, value, level };
    if (level === 'organization') {
        data.organization_id = organization;
    } else if (level === 'team') {
        data.team_ids = teams.length > 0 ? teams : [teams[0]]; // Ensure it's always an array
    }

    fetch('/api/v1/add', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => {
        if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        alert(data.message);
        // Update the dashboard dynamically
        if (data.newEntry) {
            updateDashboard(data.newEntry);
        } else {
            // If newEntry is not provided, reload the page
            window.location.reload();
        }
        // Reset form
        resetForm();
        toggleAddForm();
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

function resetForm() {
    document.getElementById('add-form').reset();
    document.getElementById('level').value = 'personal';
    toggleOrganizationTeamSelect();
}

function updateDashboard(newEntry) {
    const tableId = newEntry.level === 'organization' ? 'organization-table' :
                    newEntry.level === 'team' ? 'team-table' : 'personal-table';
    const table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    const newRow = table.insertRow();
    
    newRow.innerHTML = `
        <td>${newEntry.key}</td>
        <td>${newEntry.value}</td>
        ${newEntry.level !== 'personal' ? `<td>${newEntry.level === 'organization' ? newEntry.organization_name : newEntry.team_names.join(', ')}</td>` : ''}
        <td>
            <button class="update-button" onclick="updateValue('${newEntry.key}', '${newEntry.value}', '${newEntry.level}')">Update</button>
            <button class="delete-button" onclick="confirmDelete('${newEntry.key}', '${newEntry.level}')">Delete</button>
        </td>
    `;
}

function toggleOrganizationTeamSelect() {
    const level = document.getElementById('level').value;
    const orgSelect = document.getElementById('organization-select');
    const teamSelect = document.getElementById('team-select');
    
    orgSelect.style.display = level === 'organization' ? 'block' : 'none';
    teamSelect.style.display = level === 'team' ? 'block' : 'none';
}