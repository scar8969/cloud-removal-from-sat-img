// export.js - Download helpers

function downloadBase64(b64String, filename) {
    const link = document.createElement('a');
    link.href = b64String;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function downloadImageFromUrl(url, filename) {
    fetch(url)
        .then(r => r.blob())
        .then(blob => {
            const link = document.createElement('a');
            link.href = URL.createObjectURL(blob);
            link.download = filename;
            link.click();
            URL.revokeObjectURL(link.href);
        });
}

// Export for use in app.js
window.downloadBase64 = downloadBase64;
window.downloadImageFromUrl = downloadImageFromUrl;
