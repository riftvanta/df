// Manufacturing Workload Manager - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'))
    var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl)
    });

    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert');
        alerts.forEach(function(alert) {
            if (alert.classList.contains('alert-success') || alert.classList.contains('alert-info')) {
                var bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        });
    }, 5000);

    // Form validation enhancement
    var forms = document.querySelectorAll('.needs-validation');
    Array.prototype.slice.call(forms).forEach(function (form) {
        form.addEventListener('submit', function (event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        }, false);
    });

    // Loading spinner functions
    window.showLoading = function() {
        const spinner = document.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'block';
        }
    };

    window.hideLoading = function() {
        const spinner = document.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
    };

    // AJAX form submission helper
    window.submitForm = function(formId, successCallback, errorCallback) {
        const form = document.getElementById(formId);
        if (!form) return;

        const formData = new FormData(form);
        
        showLoading();
        
        fetch(form.action, {
            method: form.method,
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            hideLoading();
            if (data.success) {
                if (successCallback) successCallback(data);
            } else {
                if (errorCallback) errorCallback(data);
            }
        })
        .catch(error => {
            hideLoading();
            console.error('Error:', error);
            if (errorCallback) errorCallback({message: 'An error occurred'});
        });
    };

    // Time formatting helper
    window.formatHours = function(hours) {
        if (hours === null || hours === undefined) return 'N/A';
        if (hours < 1) return Math.round(hours * 60) + ' minutes';
        
        const wholeHours = Math.floor(hours);
        const minutes = Math.round((hours - wholeHours) * 60);
        
        if (minutes === 0) {
            return wholeHours + ' hours';
        } else {
            return wholeHours + ' hours, ' + minutes + ' minutes';
        }
    };

    // Status badge helper
    window.getStatusBadge = function(status) {
        const statusMap = {
            'not_started': 'status-not-started',
            'in_progress': 'status-in-progress',
            'on_hold': 'status-on-hold',
            'completed': 'status-completed',
            'at_risk': 'status-at-risk'
        };
        
        const statusLabels = {
            'not_started': 'Not Started',
            'in_progress': 'In Progress',
            'on_hold': 'On Hold',
            'completed': 'Completed',
            'at_risk': 'At Risk'
        };
        
        const badgeClass = statusMap[status] || 'badge-secondary';
        const badgeLabel = statusLabels[status] || status;
        
        return `<span class="badge ${badgeClass}">${badgeLabel}</span>`;
    };

    // Confirmation dialog helper
    window.confirmAction = function(message, callback) {
        if (confirm(message)) {
            callback();
        }
    };

    // Table sorting helper
    window.sortTable = function(table, column, ascending = true) {
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        rows.sort((a, b) => {
            const aValue = a.cells[column].textContent.trim();
            const bValue = b.cells[column].textContent.trim();
            
            if (ascending) {
                return aValue.localeCompare(bValue);
            } else {
                return bValue.localeCompare(aValue);
            }
        });
        
        tbody.innerHTML = '';
        rows.forEach(row => tbody.appendChild(row));
    };

    // Real-time updates (to be implemented with WebSockets or polling)
    window.startRealTimeUpdates = function() {
        // Placeholder for real-time functionality
        console.log('Real-time updates would be implemented here');
    };
});

// Utility functions
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
});

// Add FontAwesome icons support
document.addEventListener('DOMContentLoaded', function() {
    // Add FontAwesome CSS if not already present
    if (!document.querySelector('link[href*="fontawesome"]')) {
        const link = document.createElement('link');
        link.rel = 'stylesheet';
        link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css';
        document.head.appendChild(link);
    }
}); 