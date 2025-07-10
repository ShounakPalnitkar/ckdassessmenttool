document.addEventListener('DOMContentLoaded', function() {
    // Form interactions
    document.getElementById('diabetes').addEventListener('change', function() {
        const durationField = document.getElementById('duration');
        if (this.value === 'type1' || this.value === 'type2') {
            durationField.disabled = false;
            durationField.required = true;
        } else {
            durationField.disabled = true;
            durationField.required = false;
            durationField.value = '0';
        }
    });

    // Handle download button
    document.getElementById('download-text').addEventListener('click', function() {
        fetch('/download-report', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                // Pass necessary data for the report
            })
        })
        .then(response => response.json())
        .then(data => {
            const blob = new Blob([data.content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = data.filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    });

    // Reset button
    document.getElementById('reset-btn').addEventListener('click', function() {
        window.location.href = '/';
    });
});
