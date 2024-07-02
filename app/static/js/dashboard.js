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


function filterTable() {
    const input = document.getElementById('search-input').value.toUpperCase();
    const tables = document.querySelectorAll('table tbody');
    tables.forEach(table => {
        const rows = table.getElementsByTagName('tr');
        Array.from(rows).forEach(row => {
            const cells = row.getElementsByTagName('td');
            if (cells.length > 0 && cells[0].innerText.toUpperCase().indexOf(input) > -1) {
                row.classList.remove('hidden');
            } else {
                row.classList.add('hidden');
            }
        });
    });
}

document.addEventListener("DOMContentLoaded", function() {
    // Sidenav initialization
    const sidenav = document.getElementById('sidenav');
    const mainContent = document.getElementById('mainContent');

    // Ensure initial state of sidenav
    sidenav.classList.add('w-[60px]');
    mainContent.classList.add('ml-[60px]', 'w-[calc(100%-60px)]');

    // Setup outside click listener
    setupOutsideClickListener();

    // Remove flash messages after they fade out
    setTimeout(() => {
        const flashes = document.querySelectorAll('.flash-message');
        flashes.forEach(flash => {
            flash.style.display = 'none';
        });
    }, 5000); // Match the duration of the fadeOut animation
});

function toggleSidenav() {
    const sidenav = document.getElementById('sidenav');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.getElementById('toggleBtn');

    sidenav.classList.toggle('w-[200px]');
    mainContent.classList.toggle('ml-[200px]');
    mainContent.classList.toggle('w-[calc(100%-200px)]');

    const sidenavItems = sidenav.querySelectorAll('a span');
    sidenavItems.forEach(item => {
        item.classList.toggle('opacity-100');
        item.classList.toggle('hidden');
    });

    // Rotate the toggle button icon
    toggleBtn.querySelector('i').classList.toggle('fa-rotate-90');
}


function toggleAddForm() {
    const addForm = document.getElementById('add-form');
    if (addForm.classList.contains('hidden')) {
        addForm.classList.remove('hidden');
    } else {
        addForm.classList.add('hidden');
        resetForm();
    }
}

function setupOutsideClickListener() {
    const addForm = document.getElementById('add-form');
    const addIconContainer = document.querySelector('.fixed.bottom-5.right-5');

    document.addEventListener('click', function(event) {
        const isClickInsideForm = addForm.contains(event.target);
        const isClickOnAddIcon = addIconContainer.contains(event.target);

        if (!isClickInsideForm && !isClickOnAddIcon && !addForm.classList.contains('hidden')) {
            toggleAddForm();
        }
    });
}

function addKeyValue(event) {
    event.preventDefault();

    const key = document.getElementById('key').value;
    const value = document.getElementById('value').value;
    const level = document.getElementById('level').value;
    const organization = document.getElementById('organization')?.value;
    const teams = Array.from(document.getElementById('teams')?.selectedOptions || []).map(option => option.value);
    const submitButton = document.getElementById('add-key-value-btn');
    const buttonText = submitButton.querySelector('.button-text');
    const loadingSpinner = submitButton.querySelector('.hidden');

    // Show loading state
    buttonText.classList.add('hidden');
    loadingSpinner.classList.remove('hidden');
    submitButton.disabled = true;

    const data = { key, value, level };
    if (level === 'organization') {
        data.organization_id = organization;
    } else if (level === 'team') {
        data.team_ids = teams;
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
        document.getElementById('add-form').reset();
        toggleAddForm();
    })
    .catch(error => {
        console.error('Error:', error);
        alert(error.error || 'An error occurred while adding the key-value pair');
    })
    .finally(() => {
        // Reset button state
        buttonText.classList.remove('hidden');
        loadingSpinner.classList.add('hidden');
        submitButton.disabled = false;
    });
}

function updateDashboard(newEntry) {
    const tableId = newEntry.level === 'organization' ? 'organization-table' :
                    newEntry.level === 'team' ? 'team-table' : 'personal-table';
    const table = document.getElementById(tableId).getElementsByTagName('tbody')[0];
    const newRow = table.insertRow();
    
    newRow.innerHTML = `
        <td class="border-b border-gray-200 p-2">${newEntry.key}</td>
        <td class="border-b border-gray-200 p-2">${newEntry.value}</td>
        ${newEntry.level !== 'personal' ? `<td class="border-b border-gray-200 p-2">${newEntry.level === 'organization' ? newEntry.organization_name : newEntry.team_names.join(', ')}</td>` : ''}
        <td class="border-b border-gray-200 p-2">
            <button class="bg-yellow-500 text-white px-2 py-1 rounded text-sm hover:bg-yellow-600 transition-colors" onclick="updateValue('${newEntry.key}', '${newEntry.value}')">Update</button>
            <button class="bg-red-500 text-white px-2 py-1 rounded text-sm hover:bg-red-600 transition-colors ml-2" onclick="confirmDelete('${newEntry.key}')">Delete</button>
        </td>
    `;
}

function resetForm() {
    const form = document.getElementById('add-form');
    form.reset();
    document.getElementById('level').value = 'personal';
    toggleOrganizationTeamSelect();
}

function toggleOrganizationTeamSelect() {
    const level = document.getElementById('level').value;
    const orgSelect = document.getElementById('organization-select');
    const teamSelect = document.getElementById('team-select');
    
    orgSelect.classList.toggle('hidden', level !== 'organization');
    teamSelect.classList.toggle('hidden', level !== 'team');
}