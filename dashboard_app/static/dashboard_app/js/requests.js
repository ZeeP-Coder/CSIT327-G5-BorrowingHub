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

    approveButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
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
                    alert(data.message || 'Request approved');
                    location.reload();
                } else {
                    alert(data.error || 'Error approving request');
                }
            })
            .catch(err => {
                console.error(err);
                alert('Network error');
            });
        });
    });

    rejectButtons.forEach(button => {
        button.addEventListener('click', function() {
            const url = this.dataset.url;
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
                    alert(data.message || 'Request rejected');
                    location.reload();
                } else {
                    alert(data.error || 'Error rejecting request');
                }
            })
            .catch(err => {
                console.error(err);
                alert('Network error');
            });
        });
    });

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