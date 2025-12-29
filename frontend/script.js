/**
 * Check if backend is running and display connection status
 * This function runs when the page loads
 */
async function checkBackendConnection() {
    const statusElement = document.getElementById('backend-status');
    
    try {
        // Make a GET request to the health check endpoint
        const response = await fetch('/health');
        
        // Check if response is successful (status code 200-299)
        if (response.ok) {
            const data = await response.json();
            statusElement.textContent = `✓ Backend Connected: ${data.message}`;
            statusElement.classList.add('connected');
        } else {
            throw new Error('Backend returned non-OK status');
        }
    } catch (error) {
        // If fetch fails (network error, backend down, etc.)
        statusElement.textContent = '✗ Backend connection failed. Make sure the server is running.';
        statusElement.classList.add('error');
        console.error('Backend connection error:', error);
    }
}

// Run the connection check when the page fully loads
window.addEventListener('DOMContentLoaded', checkBackendConnection);