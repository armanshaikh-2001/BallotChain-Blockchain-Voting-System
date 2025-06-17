// Global functions used across all pages

// Initialize tooltips
document.addEventListener('DOMContentLoaded', function() {
    // Add any global initialization code here
    console.log('BallotChain initialized');
    
    // Set current year in footer
    document.querySelector('footer p').innerHTML = `BallotChain &copy; ${new Date().getFullYear()} - Blockchain Voting System`;
});

// Helper function for showing loading states
function showLoading(element) {
    const originalContent = element.innerHTML;
    element.innerHTML = '<div class="loading-spinner"></div>';
    element.disabled = true;
    return originalContent;
}

function hideLoading(element, originalContent) {
    element.innerHTML = originalContent;
    element.disabled = false;
}

// Flash message auto-dismiss
const flashMessages = document.querySelectorAll('.flash');
if (flashMessages.length > 0) {
    flashMessages.forEach(flash => {
        setTimeout(() => {
            flash.style.opacity = '0';
            setTimeout(() => flash.remove(), 300);
        }, 5000);
    });
}