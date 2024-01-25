// This script file would be linked in your base.html and used if you need any client-side JavaScript.
// For example, you might want to confirm before saving the changes:

document.addEventListener('DOMContentLoaded', function() {
    const accountForm = document.getElementById('account-form');
    accountForm.addEventListener('submit', function(event) {
        if (!confirm('Are you sure you want to save these changes?')) {
            event.preventDefault();
        }
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const accountForm = document.getElementById('add-metric-form');
    accountForm.addEventListener('submit', function(event) {
        if (!confirm('Are you sure you want to save these changes?')) {
            event.preventDefault();
        }
    });
});