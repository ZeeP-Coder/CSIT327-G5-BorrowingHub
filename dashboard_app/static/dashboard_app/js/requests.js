document.addEventListener('DOMContentLoaded', function() {
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

    const approveButtons = document.querySelectorAll('.approve-request');
    const rejectButtons = document.querySelectorAll('.reject-request');

    // Toast notification function
    function showNotification(message, type = 'success') {
        // Remove any existing notification
        const existingToast = document.querySelector('.toast-notification');
        if (existingToast) {
            existingToast.remove();
        }

        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <i class="fa-solid ${type === 'success' ? 'fa-circle-check' : 'fa-circle-exclamation'}"></i>
            <span>${message}</span>
        `;
        document.body.appendChild(toast);

        // Trigger animation
        setTimeout(() => toast.classList.add('show'), 10);

        // Remove after 3 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            this.disabled = true;
            this.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Approving...';
            
            fetch(url, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showNotification('Request approved successfully', 'success');
                    setTimeout(() => location.reload(), 800);
                } else {
                    showNotification(data.error || 'Error approving request', 'error');
                    this.disabled = false;
                    this.innerHTML = '<i class="fa-solid fa-check"></i> Approve';
                }
            })
            .catch(err => {
                console.error(err);
                showNotification('Network error occurred', 'error');
                this.disabled = false;
                this.innerHTML = '<i class="fa-solid fa-check"></i> Approve';
            });
        });
    });

    // Rejection Modal functionality
    const rejectionModal = document.getElementById('rejectionModal');
    const rejectionForm = document.getElementById('rejectionForm');
    const rejectionItemName = document.getElementById('rejectionItemName');
    const rejectionBorrowerName = document.getElementById('rejectionBorrowerName');
    const rejectionReason = document.getElementById('rejectionReason');
    const closeRejectionModal = document.getElementById('closeRejectionModal');
    const cancelRejection = document.getElementById('cancelRejection');
    const rejectionModalOverlay = document.getElementById('rejectionModalOverlay');
    
    let currentRejectUrl = null;
    
    function openRejectionModal(itemName, borrowerName, url) {
        rejectionItemName.textContent = itemName;
        rejectionBorrowerName.textContent = borrowerName;
        currentRejectUrl = url;
        rejectionReason.value = '';
        rejectionModal.style.display = 'flex';
        rejectionModal.setAttribute('aria-hidden', 'false');
        rejectionReason.focus();
    }
    
    function closeRejectionModalFunc() {
        rejectionModal.style.display = 'none';
        rejectionModal.setAttribute('aria-hidden', 'true');
        currentRejectUrl = null;
    }
    
    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
            const itemName = this.dataset.itemName;
            const borrowerName = this.dataset.borrowerName;
            openRejectionModal(itemName, borrowerName, url);
        });
    });
    
    if (closeRejectionModal) {
        closeRejectionModal.addEventListener('click', closeRejectionModalFunc);
    }
    if (cancelRejection) {
        cancelRejection.addEventListener('click', closeRejectionModalFunc);
    }
    if (rejectionModalOverlay) {
        rejectionModalOverlay.addEventListener('click', closeRejectionModalFunc);
    }
    
    if (rejectionForm) {
        rejectionForm.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!currentRejectUrl) return;
            
            const reason = rejectionReason.value.trim();
            const confirmBtn = document.getElementById('confirmRejection');
            confirmBtn.disabled = true;
            confirmBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Rejecting...';
            
            fetch(currentRejectUrl, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCookie('csrftoken'),
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ reason: reason })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    closeRejectionModalFunc();
                    // Show success message inline instead of alert
                    showNotification('Request rejected successfully', 'success');
                    setTimeout(() => location.reload(), 800);
                } else {
                    showNotification(data.error || 'Error rejecting request', 'error');
                    confirmBtn.disabled = false;
                    confirmBtn.innerHTML = '<i class="fa-solid fa-ban"></i> Reject Request';
                }
            })
            .catch(err => {
                console.error(err);
                showNotification('Network error occurred', 'error');
                confirmBtn.disabled = false;
                confirmBtn.innerHTML = '<i class="fa-solid fa-ban"></i> Reject Request';
            });
        });
    }

    // Modal open/close handlers
    const openBtn = document.getElementById('openRequestsModal');
    const closeBtn = document.getElementById('closeRequestsModal');
    const modal = document.getElementById('requestsModal');

    function openModal() {
        if (modal) {
            modal.style.display = 'block';
            modal.setAttribute('aria-hidden', 'false');
        }
    }
    function closeModal() {
        if (modal) {
            modal.style.display = 'none';
            modal.setAttribute('aria-hidden', 'true');
        }
    }

    if (openBtn) openBtn.addEventListener('click', openModal);
    if (closeBtn) closeBtn.addEventListener('click', closeModal);
    // close on ESC
    document.addEventListener('keydown', function(e) { if (e.key === 'Escape') closeModal(); });
});