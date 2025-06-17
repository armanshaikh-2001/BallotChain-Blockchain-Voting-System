// Admin-specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any admin-specific functionality
    
    // Handle candidate image preview
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(event) {
                    const preview = document.getElementById('image-preview');
                    if (!preview) {
                        const previewContainer = document.createElement('div');
                        previewContainer.id = 'image-preview-container';
                        const previewImg = document.createElement('img');
                        previewImg.id = 'image-preview';
                        previewImg.src = event.target.result;
                        previewImg.style.maxWidth = '200px';
                        previewImg.style.marginTop = '10px';
                        previewContainer.appendChild(previewImg);
                        imageInput.parentNode.appendChild(previewContainer);
                    } else {
                        preview.src = event.target.result;
                    }
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Handle voter import/export tabs
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
    
    // Handle blockchain verification alerts
    const verifyBtn = document.querySelector('.btn-verify');
    if (verifyBtn) {
        verifyBtn.addEventListener('click', function(e) {
            // This would typically be handled server-side, just UI here
            console.log('Blockchain verification requested');
        });
    }
});