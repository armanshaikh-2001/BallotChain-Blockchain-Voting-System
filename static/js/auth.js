// Authentication page JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Handle tab switching on login page
    const tabButtons = document.querySelectorAll('.tab-button');
    if (tabButtons.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', function() {
                // Remove active class from all buttons and content
                document.querySelectorAll('.tab-button').forEach(btn => btn.classList.remove('active'));
                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                
                // Add active class to clicked button and corresponding content
                this.classList.add('active');
                const tabId = this.getAttribute('data-tab') + '-tab';
                document.getElementById(tabId).classList.add('active');
            });
        });
    }
    
    // Focus on first input field
    const firstInput = document.querySelector('input');
    if (firstInput) {
        firstInput.focus();
    }
    
    // Handle form submission
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitButton = this.querySelector('button[type="submit"]');
            if (submitButton) {
                const originalContent = showLoading(submitButton);
                
                // Simulate network delay for demo
                setTimeout(() => {
                    hideLoading(submitButton, originalContent);
                }, 1000);
            }
        });
    });
});