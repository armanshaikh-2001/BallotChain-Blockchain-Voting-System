// Voter-specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any voter-specific functionality
    
    // Handle vote confirmation
    const voteButtons = document.querySelectorAll('.btn-vote');
    if (voteButtons.length > 0) {
        voteButtons.forEach(button => {
            button.addEventListener('click', function(e) {
                const candidateName = this.textContent.replace('Vote for ', '');
                const confirmed = confirm(`Are you sure you want to vote for ${candidateName}? This action cannot be undone.`);
                
                if (!confirmed) {
                    e.preventDefault();
                }
            });
        });
    }
    
    // Handle receipt download
    const downloadBtn = document.querySelector('.btn-download');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', function() {
            // Track download in analytics if needed
            console.log('Receipt downloaded');
        });
    }
    
    // Animate candidate cards on hover
    const candidateCards = document.querySelectorAll('.candidate-card');
    candidateCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 20px rgba(0, 0, 0, 0.1)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
});