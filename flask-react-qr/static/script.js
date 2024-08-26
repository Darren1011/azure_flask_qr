document.getElementById('qrForm').addEventListener('submit', function(event) {
    event.preventDefault(); // Prevent the form from submitting the traditional way

    const formData = new FormData(this);

    fetch('/generate-qr', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            document.getElementById('qrImage').src = data.imageUrl;
        } else {
            alert('Failed to generate QR code');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});