function checkOllamaStatus() {
    const statusIndicator = document.getElementById('ollama-status');

    // Simulating a status check (you can replace this with actual logic like an API call)
    setInterval(() => {
        // Example logic for status check
        const isOnline = Math.random() > 0.5;  // Randomly simulate online/offline status

        if (isOnline) {
            statusIndicator.textContent = 'Ollama is online';
            statusIndicator.style.backgroundColor = '#28a745';  // Green for online
            statusIndicator.style.color = 'white';
        } else {
            statusIndicator.textContent = 'Ollama is offline';
            statusIndicator.style.backgroundColor = '#dc3545';  // Red for offline
            statusIndicator.style.color = 'white';
        }
    }, 5000);  // Check status every 5 seconds
}
