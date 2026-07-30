document.addEventListener('DOMContentLoaded', () => {
    // Alert close utility with fading
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        }, 5000);
    });

    // DB Tamper simulation
    const tamperBtn = document.getElementById('tamper-btn');
    if (tamperBtn) {
        tamperBtn.addEventListener('click', async () => {
            if (confirm('Are you sure you want to simulate database tampering? This will directly modify a description in the SQL database without recalculating the hashes, which will break the blockchain integrity.')) {
                tamperBtn.disabled = true;
                tamperBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Tampering...';
                
                try {
                    const response = await fetch('/admin/tamper', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        }
                    });
                    const data = await response.json();
                    
                    if (response.ok) {
                        alert(data.message);
                        window.location.reload();
                    } else {
                        alert('Error: ' + data.error);
                        tamperBtn.disabled = false;
                        tamperBtn.innerHTML = 'Simulate DB Tampering';
                    }
                } catch (err) {
                    console.error('Tampering error:', err);
                    alert('An error occurred while attempting to simulate tampering.');
                    tamperBtn.disabled = false;
                    tamperBtn.innerHTML = 'Simulate DB Tampering';
                }
            }
        });
    }

    // DB Restore simulation
    const restoreBtn = document.getElementById('restore-btn');
    if (restoreBtn) {
        restoreBtn.addEventListener('click', async () => {
            restoreBtn.disabled = true;
            restoreBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Restoring...';
            
            try {
                const response = await fetch('/admin/restore', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    }
                });
                const data = await response.json();
                
                if (response.ok) {
                    alert(data.message);
                    window.location.reload();
                } else {
                    alert('Error: ' + data.error);
                    restoreBtn.disabled = false;
                    restoreBtn.innerHTML = 'Restore Blockchain Integrity';
                }
            } catch (err) {
                console.error('Restoration error:', err);
                alert('An error occurred while attempting to restore the blockchain.');
                restoreBtn.disabled = false;
                restoreBtn.innerHTML = 'Restore Blockchain Integrity';
            }
        });
    }
});
