# `script.js` Documentation

## Overview
This JavaScript file implements the main functionality for the file upload and processing system in the Customer Churn Prediction application. It handles user interactions with the drag-and-drop file upload interface, file validation, and communication with the backend API.

## Key Features
- Drag-and-drop file upload for three different file types (audio, data, chat)
- File type validation for each upload area
- Visual feedback during drag operations
- File list management with remove capabilities
- File size formatting
- Confirmation modals before upload
- Loading spinner during processing
- Results display with formatted output

## Global Variables

### File Storage
```javascript
const files = {
  audio: [],
  data: [],
  chat: [],
};
```
Stores uploaded files by category before sending to the server.

### DOM References
```javascript
const dropAreas = {
  audio: document.getElementById("audio-drop-area"),
  data: document.getElementById("data-drop-area"),
  chat: document.getElementById("chat-drop-area"),
};

const fileInputs = {
  audio: document.getElementById("audioFileInput"),
  data: document.getElementById("dataFileInput"),
  chat: document.getElementById("chatFileInput"),
};
```
References to critical DOM elements for file uploads and UI interaction.

## Core Functions

### Event Handling

#### `preventDefaults(e)`
Prevents default browser behavior for drag events to ensure proper drag-and-drop functionality.

#### `highlight(type)` / `unhighlight(type)`
Provides visual feedback by changing the background color and border of drop areas during drag operations.

#### `handleDrop(e, type)`
Processes files dropped onto a specific drop area.
```javascript
function handleDrop(e, type) {
  const dt = e.dataTransfer;
  const droppedFiles = dt.files;
  handleFiles(droppedFiles, type);
}
```

### File Processing

#### `handleFiles(fileList, type)`
Processes and validates uploaded files:
- Checks file extensions against allowed types
- Prevents duplicate files
- Adds valid files to the appropriate category
- Updates the file list display
```javascript
const allowedExtensions = {
  audio: [".mp3", ".wav"],
  data: [".csv", ".xlsx"],
  chat: [".docx", ".txt"],
};
```

#### `updateFileList(type)`
Refreshes the visual display of uploaded files in each category:
- Clears existing file list
- Generates HTML for each file with name and size
- Adds remove buttons with event listeners
```javascript
files[type].forEach((file, index) => {
  const fileItem = document.createElement("div");
  fileItem.className = "file-list-item";
  // Generate file item HTML
});
```

#### `updateSubmitButton()`
Enables or disables the submit button based on whether any files have been uploaded.

#### `formatBytes(bytes, decimals = 2)`
Formats file sizes into human-readable format (KB, MB, GB, etc.).
```javascript
const sizes = ["Bytes", "KB", "MB", "GB", "TB"];
const i = Math.floor(Math.log(bytes) / Math.log(k));
return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
```

### Upload Process

#### `submitButtonEvent()`
Triggered when the "Upload All Files" button is clicked:
- Counts files by category
- Populates and displays the confirmation modal
```javascript
const counts = {
  audio: files.audio.length,
  data: files.data.length,
  chat: files.chat.length,
};
```

#### `handleUpload()`
Performs the actual file upload to the server:
- Shows loading spinner
- Creates FormData with all files
- Adds CSRF token for security
- Sends data to the server via fetch API
- Processes and displays the results
```javascript
fetch("/upload", {
  method: "POST",
  body: formData,
  headers: {
    "X-CSRFToken": csrfToken || "",
  },
  credentials: "same-origin",
})
```

### Results Display

#### `showNotificationModal(result)`
Displays analysis results in a formatted modal:
- Parses structured data or email template format
- Formats results for visual display with color coding
- Applies custom CSS styles for the results
```javascript
const readableText = formatResultsHTML(
  result.audio_output,
  dataOutput,
  result.chat_output,
  result.final_decision,
  new Date().toLocaleString(),
  result.triggered_by || 'System'
);
```

#### `formatResultsHTML(audioOutput, dataOutput, chatOutput, finalDecision, timestamp, userName)`
Generates standardized HTML for displaying the analysis results.

#### `formatDataOutput(dataModel)`
Formats data model results with proper styling:
- Handles array of prediction results
- Formats probabilities as percentages
- Adds color coding for STAY/CHURN predictions
```javascript
if (Array.isArray(dataModel)) {
  return dataModel.map(item => {
    // Format each prediction result
  }).join("");
}
```

### Loading Indicators

#### `showSpinner()` / `hideSpinner()`
Controls the visibility of the loading spinner during API calls.

## Event Listeners

### Initialization
The script sets up multiple event listeners during initialization:
- Drag-and-drop events for each upload area
- File input change events
- Button click events with visual feedback
- Modal close buttons and background click handling

### Modal Controls
```javascript
// Handling OK button
document.getElementById("okButton").onclick = function () {
  document.getElementById("notificationModal").style.display = "none";
};
```

## Error Handling
- Validation errors show alerts for incorrect file types
- Network errors display alerts with error messages
- Console logging for debugging purposes
- Fallback display logic when result format is unexpected

## Integration Points
- Communicates with the server via POST to `/upload` endpoint
- Expects JSON response with structured data
- Supports CSRF protection with tokens