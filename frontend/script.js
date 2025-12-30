/**
 * Check if backend is running and display connection status
 */
async function checkBackendConnection() {
    const statusElement = document.getElementById('backend-status');
    
    try {
        const response = await fetch('/health');
        
        if (response.ok) {
            const data = await response.json();
            statusElement.textContent = `✓ Backend Connected: ${data.message}`;
            statusElement.classList.add('connected');
        } else {
            throw new Error('Backend returned non-OK status');
        }
    } catch (error) {
        statusElement.textContent = '✗ Backend connection failed. Make sure the server is running.';
        statusElement.classList.add('error');
        console.error('Backend connection error:', error);
    }
}

/**
 * Handle file selection and update UI
 */
function handleFileSelect(inputId, displayId) {
    const input = document.getElementById(inputId);
    const display = document.getElementById(displayId);
    
    // Listen for file selection changes
    input.addEventListener('change', function(event) {
        const file = event.target.files[0];
        
        if (file) {
            // Show file name and size
            const fileSizeMB = (file.size / (1024 * 1024)).toFixed(2);
            display.textContent = `${file.name} (${fileSizeMB} MB)`;
            display.classList.add('file-selected');
        } else {
            // Reset if no file selected
            display.textContent = 'No file selected';
            display.classList.remove('file-selected');
        }
        
        // Check if both files are selected to enable upload button
        checkBothFilesSelected();
    });
}

/**
 * Check if both files are selected and enable/disable upload button
 */
function checkBothFilesSelected() {
    const pdfFile = document.getElementById('pdfFile').files[0];
    const masterFile = document.getElementById('masterFile').files[0];
    const uploadBtn = document.getElementById('uploadBtn');
    
    // Enable button only if both files are selected
    if (pdfFile && masterFile) {
        uploadBtn.disabled = false;
    } else {
        uploadBtn.disabled = true;
    }
}

/**
 * Display status message to user
 */
function showStatus(message, type) {
    const statusElement = document.getElementById('uploadStatus');
    
    // Remove all existing classes
    statusElement.className = 'upload-status';
    
    // Add new classes based on type
    statusElement.classList.add('show', type);
    statusElement.textContent = message;
}

/**
 * Handle file upload to backend
 */
async function handleUpload() {
    const pdfFile = document.getElementById('pdfFile').files[0];
    const masterFile = document.getElementById('masterFile').files[0];
    const uploadBtn = document.getElementById('uploadBtn');
    
    // Validate files exist (should always be true because button is disabled otherwise)
    if (!pdfFile || !masterFile) {
        showStatus('Please select both files', 'error');
        return;
    }
    
    // Validate file types
    if (!pdfFile.name.toLowerCase().endsWith('.pdf')) {
        showStatus('Please select a valid PDF file', 'error');
        return;
    }
    
    const masterFileExt = masterFile.name.toLowerCase();
    if (!masterFileExt.endsWith('.xlsx') && !masterFileExt.endsWith('.xls') && !masterFileExt.endsWith('.csv')) {
        showStatus('Please select a valid Excel or CSV file', 'error');
        return;
    }
    
    // Show loading state
    uploadBtn.disabled = true;
    uploadBtn.classList.add('loading');
    uploadBtn.textContent = 'Uploading...';
    showStatus('Uploading files to server...', 'loading');
    
    try {
        // Create FormData object to send files
        const formData = new FormData();
        formData.append('pdf_file', pdfFile);
        formData.append('master_file', masterFile);
        
        // Send files to backend
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
            // Note: Don't set Content-Type header - browser sets it automatically with boundary
        });
        
        // Parse response
        const result = await response.json();
        
        if (response.ok) {
            // Success
            showStatus(result.message || 'Files uploaded successfully!', 'success');
            console.log('Upload response:', result);
        } else {
            // Server returned an error
            showStatus(result.detail || 'Upload failed. Please try again.', 'error');
        }
        
    } catch (error) {
        // Network error or other exception
        console.error('Upload error:', error);
        showStatus('Network error. Please check your connection and try again.', 'error');
    } finally {
        // Reset button state
        uploadBtn.disabled = false;
        uploadBtn.classList.remove('loading');
        uploadBtn.textContent = 'Upload & Process';
    }
}

/**
 * Initialize the application when DOM is loaded
 */
function initializeApp() {
    // Check backend connection
    checkBackendConnection();
    
    // Set up file input handlers
    handleFileSelect('pdfFile', 'pdfFileName');
    handleFileSelect('masterFile', 'masterFileName');
    
    // Set up upload button click handler
    const uploadBtn = document.getElementById('uploadBtn');
    uploadBtn.addEventListener('click', handleUpload);
}

// Run initialization when page loads
window.addEventListener('DOMContentLoaded', initializeApp);