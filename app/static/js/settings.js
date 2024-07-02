// settings.js
document.addEventListener('DOMContentLoaded', function() {
    const openAddUserDialog = document.getElementById('openAddUserDialog');
    const addUserDialog = document.getElementById('addUserDialog');
    const addUserForm = document.getElementById('addUserForm');

    if (openAddUserDialog && addUserDialog && addUserForm) {
        openAddUserDialog.addEventListener('click', () => {
            addUserDialog.classList.remove('hidden');
        });

        addUserDialog.addEventListener('click', (e) => {
            if (e.target === addUserDialog) {
                addUserDialog.classList.add('hidden');
            }
        });

        addUserForm.addEventListener('submit', () => {
            addUserDialog.classList.add('hidden');
        });
    }
});