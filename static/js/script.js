// File storage by category
const files = {
  audio: [],
  data: [],
  chat: [],
};

// Getting elements
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

const fileContainers = {
  audio: document.getElementById("audioFiles"),
  data: document.getElementById("dataFiles"),
  chat: document.getElementById("chatFiles"),
};

const submitBtn = document.getElementById("submitBtn");
const continueBtn = document.getElementById("continueButton");

// Setting up drag and drop for each area
Object.keys(dropAreas).forEach((type) => {
  const dropArea = dropAreas[type];

  // Preventing default drag behaviors
  ["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(eventName, preventDefaults, false);
  });

  // Highlighting drop area when item is dragged over it
  ["dragenter", "dragover"].forEach((eventName) => {
    dropArea.addEventListener(
      eventName,
      function () {
        highlight(type);
      },
      false
    );
  });

  // Removing highlight when item is dragged away
  ["dragleave", "drop"].forEach((eventName) => {
    dropArea.addEventListener(
      eventName,
      function () {
        unhighlight(type);
      },
      false
    );
  });

  // Handling dropped files
  dropArea.addEventListener(
    "drop",
    function (e) {
      handleDrop(e, type);
    },
    false
  );
});

// Global prevent default for drag events
["dragenter", "dragover", "dragleave", "drop"].forEach((eventName) => {
  document.body.addEventListener(eventName, preventDefaults, false);
});

// File input change handlers
Object.keys(fileInputs).forEach((type) => {
  fileInputs[type].addEventListener(
    "change",
    function (e) {
      handleFiles(e.target.files, type);
      fileInputs[type].value = "";
    },
    false
  );
});

// Click "Select Data Files" button event -> color change
document.querySelectorAll(".colorBtn").forEach((button) => {
  button.addEventListener("click", function () {
    const originalColor = this.style.backgroundColor;
    this.style.backgroundColor = "#9e9b9b";

    setTimeout(() => {
      this.style.backgroundColor = originalColor || "";
    }, 100);
  });
});

// Submit button click event -> color change
document.querySelectorAll(".submit-btn").forEach((button) => {
  button.addEventListener("click", function () {
    const originalColor = this.style.backgroundColor;

    this.style.backgroundColor = "#115114";

    setTimeout(() => {
      this.style.backgroundColor = originalColor || "";
    }, 100);
  });
});

// "Upload All Files" button event
submitBtn.addEventListener("click", submitButtonEvent, false);

// "Continue Upload" button event
continueBtn.addEventListener("click", handleUpload, false);

function preventDefaults(e) {
  e.preventDefault();
  e.stopPropagation();
}

function highlight(type) {
  if (type === 'data') {
    // Use the blue/purple gradient for data section
    dropAreas[type].style.background = "linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%)";
    dropAreas[type].style.borderColor = "#3f51b5";
  } else {
    // Default for other sections
    dropAreas[type].style.backgroundColor = "#e0e0e0";
  }
  dropAreas[type].style.borderStyle = "solid";
}

function unhighlight(type) {
  if (type === 'data') {
    // Use lighter blue/purple for data section when not active
    dropAreas[type].style.background = "linear-gradient(135deg, #f5f6ff 0%, #e8eaf6 100%)";
    dropAreas[type].style.borderColor = "#3f51b5";
  } else {
    // Default for other sections
    dropAreas[type].style.backgroundColor = "#f9f9f9";
  }
  dropAreas[type].style.borderStyle = "dashed";
}

function handleDrop(e, type) {
  const dt = e.dataTransfer;
  const droppedFiles = dt.files;
  handleFiles(droppedFiles, type);
}

function handleFiles(fileList, type) {
  // Defining allowed extensions for each type
  const allowedExtensions = {
    audio: [".mp3", ".wav"],
    data: [".csv", ".xlsx"],
    chat: [".docx", ".txt"],
  };

  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];
    const extension = "." + file.name.split(".").pop().toLowerCase();

    // Checking if file type is allowed in this section
    if (allowedExtensions[type].includes(extension)) {
      // Adding file if not already in the list
      if (
        !files[type].some((f) => f.name === file.name && f.size === file.size)
      ) {
        files[type].push(file);
      }
    } else {
      alert(`File type ${extension} is not accepted in the ${type} section!`);
    }
  }

  updateFileList(type);
  updateSubmitButton();
}

function updateFileList(type) {
  const container = fileContainers[type];
  container.innerHTML = "";

  if (files[type].length === 0) {
    container.innerHTML = "<p><b>No files selected</b></p>";
    return;
  }

  files[type].forEach((file, index) => {
    const fileItem = document.createElement("div");
    fileItem.className = "file-list-item";

    // Converting bytes to readable format
    const size = formatBytes(file.size);

    fileItem.innerHTML = `
            <div class="file-info">
                <strong>${file.name}</strong> (${size})
            </div>
            <button class="file-remove" data-type="${type}" data-index="${index}">Remove</button>
        `;

    container.appendChild(fileItem);
  });

  // Adding event listeners to remove buttons
  document
    .querySelectorAll(`.file-remove[data-type="${type}"]`)
    .forEach((button) => {
      button.addEventListener("click", function () {
        const index = parseInt(this.getAttribute("data-index"));
        const fileType = this.getAttribute("data-type");
        files[fileType].splice(index, 1);
        updateFileList(fileType);
        updateSubmitButton();
      });
    });
}

function updateSubmitButton() {
  const totalFiles = files.audio.length + files.data.length + files.chat.length;
  submitBtn.disabled = totalFiles === 0;
}

function formatBytes(bytes, decimals = 2) {
  if (bytes === 0) return "0 Bytes";

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ["Bytes", "KB", "MB", "GB", "TB"];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + " " + sizes[i];
}

function submitButtonEvent() {
  // Getting total count of files by category
  const counts = {
    audio: files.audio.length,
    data: files.data.length,
    chat: files.chat.length,
  };

  const totalFiles = counts.audio + counts.data + counts.chat;

  // Look for customer ID in data files preview (first file only)
  let customerIdPreview = "Unknown";
  if (files.data.length > 0) {
    // We'll try to guess the customer ID during upload summary
    // This is just for UI preview, the actual ID will be extracted by the backend
    customerIdPreview = "Will be extracted during processing";
  }

  // Populating modal content
  const modalContent = document.getElementById("modalContent");
  modalContent.innerHTML = `
    <p>Ready to upload <b>${totalFiles}</b> file(s):</p>
    <ul>
      <li>Audio files: <b>${counts.audio}</b></li>
      <li>Data files: <b>${counts.data}</b></li>
      <li>Chat history files: <b>${counts.chat}</b></li>
    </ul>
    <div class="customer-preview">
      <p>Customer ID: <b>${customerIdPreview}</b></p>
    </div>
  `;

  // Showing upload files modal
  const modal = document.getElementById("uploadModal");
  modal.style.display = "flex";

  // Handling continue button
  const continueButton = document.getElementById("continueButton");
  continueButton.onclick = function () {
    // Hiding upload files modal
    modal.style.display = "none";
  };

  // Handling close button
  const closeButton = document.querySelector(".close-button");
  closeButton.onclick = function () {
    // Hiding upload files modal
    modal.style.display = "none";
  };

  // Closing upload files modal when clicking outside
  window.onclick = function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  };
}

function showSpinner() {
  document.getElementById("spinnerOverlay").style.display = "flex";
}

function hideSpinner() {
  document.getElementById("spinnerOverlay").style.display = "none";
}

function showNotificationModal(result) {
  // Formatting data output properly
  let dataOutput;
  let customerID = "Unknown";

  // Extract customer ID if available
  if (result.customer_id) {
    customerID = result.customer_id;
  }

  // Checking if result has raw email template format and parse it
  if (
    typeof result === "string" &&
    result.includes("📋 Model Results Summary")
  ) {
    // Parsing the email template into structured data
    const parsedResult = parseEmailTemplate(result);

    // Creating structured display from parsed data
    dataOutput = formatDataOutput(parsedResult.dataModel);

    const readableText = formatResultsHTML(
      parsedResult.audioModel || "N/A",
      dataOutput,
      parsedResult.chatModel || "N/A",
      parsedResult.finalDecision || "No final decision available",
      parsedResult.timestamp || new Date().toLocaleString(),
      parsedResult.user || "Unknown",
      customerID
    );
    document.getElementById("notificationContent").innerHTML = readableText;
  } else {
    // Handling structured JSON result directly
    if (Array.isArray(result.data_output)) {
      dataOutput = formatDataOutput(result.data_output);
    } else {
      dataOutput = result.data_output;
    }

    // Get customer ID from the result if available
    if (result.customer_id) {
      customerID = result.customer_id;
    }

    const readableText = formatResultsHTML(
      result.audio_output,
      dataOutput,
      result.chat_output,
      result.final_decision,
      new Date().toLocaleString(),
      result.triggered_by || "System",
      customerID
    );

    document.getElementById("notificationContent").innerHTML = readableText;
  }

  // Adding CSS styles for the notification
  applyResultStyles();

  document.getElementById("notificationModal").style.display = "flex";
}

// Helper function to create consistent HTML for results
function formatResultsHTML(
  audioOutput,
  dataOutput,
  chatOutput,
  finalDecision,
  timestamp,
  userName,
  customerID = "Unknown"
) {
  return `
    <div class="results-container">
      <div class="customer-id-section">
        <h3>Customer ID</h3>
        <div class="result-content customer-id-content"><p>${customerID}</p></div>
      </div>
      
      <div class="result-section audio-section">
        <h3>Audio Analysis</h3>
        <div class="result-content"><p>${audioOutput}</p></div>
      </div>
      
      <div class="result-section data-section">
        <h3>Data Analysis</h3>
        <div class="result-content"><p>${dataOutput}</p></div>
      </div>
      
      <div class="result-section chat-section">
        <h3>Chat Analysis</h3>
        <div class="result-content ${
          chatOutput === "NEGATIVE"
            ? "result-negative"
            : chatOutput === "POSITIVE"
            ? "result-positive"
            : ""
        }"><p>${chatOutput}</p></div>
      </div>
      
      <div class="result-section final-result">
        <h3>Final Result</h3>
        <div class="result-content"><p><b>${finalDecision}</b></p></div>
      </div>
      
      <div class="timestamp">Processed at: ${timestamp}</div>
    </div>
  `;
}

// Helper function to apply styles
function applyResultStyles() {
  // Remove any existing result styles first
  const existingStyle = document.getElementById("result-styles");
  if (existingStyle) {
    existingStyle.remove();
  }
  
  const style = document.createElement("style");
  style.id = "result-styles"; // Add an ID to the style element
  style.textContent = `
    .results-container {
      font-family: Arial, sans-serif;
      max-width: 600px;
      margin: 0 auto;
    }
    .result-section, .customer-id-section {
      margin-bottom: 20px;
      background: #ffffff;
      border-radius: 8px;
      padding: 15px;
      box-shadow: 0 3px 8px rgba(0,0,0,0.15);
      border: 1px solid #e0e0e0;
    }
    .result-section h3, .customer-id-section h3 {
      margin-top: 0;
      color: #333;
      border-bottom: 2px solid #ddd;
      padding-bottom: 8px;
      font-size: 18px;
      font-weight: 600;
    }    .customer-id-section {
      background: linear-gradient(135deg, #e1bee7 0%, #ce93d8 100%);
      border-left: 4px solid #9c27b0;
    }
    .customer-id-content {
      font-weight: bold;
      font-size: 18px;
      text-align: center;
    }    .final-result {
      background: linear-gradient(135deg, #e7f5e7 0%, #d4ecd4 100%);
      border-left: 4px solid #4CAF50;
    }    .customer-preview {
      background-color: #e8eaf6;
      padding: 10px;
      border-radius: 5px;
      margin-top: 15px;
      border-left: 4px solid #3f51b5;
    }
    /* Audio section styling */
    .audio-section {
      background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
      border-left: 4px solid #2196F3;
    }
    /* Data section styling */
    .data-section {
      background: linear-gradient(135deg, #e8eaf6 0%, #c5cae9 100%);
      border-left: 4px solid #3f51b5;
    }
    /* Chat section styling */
    .chat-section {
      background: linear-gradient(135deg, #fff8e1 0%, #ffecb3 100%);
      border-left: 4px solid #FFC107;
    }
    .result-content {
      padding: 8px 0;
      font-size: 15px;
    }
    .result-card {
      background: white;
      border-radius: 6px;
      margin-bottom: 10px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
      overflow: hidden;
      border: 1px solid #eaeaea;
    }
    .result-header {
      background: #f5f5f5;
      padding: 10px 12px;
      font-weight: bold;
      border-bottom: 1px solid #e0e0e0;
      color: #333;
    }
    .result-body {
      padding: 12px;
      line-height: 1.5;
    }
    .result-stay {
      color: #2e7d32;
      font-weight: bold;
      background-color: rgba(46, 125, 50, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
    }
    .result-churn {
      color: #c62828;
      font-weight: bold;
      background-color: rgba(198, 40, 40, 0.1);
      padding: 2px 6px;
      border-radius: 4px;
    }    .result-positive {
      color: #2e7d32;
      font-weight: bold;
    }
    .result-negative {
      color: #c62828;
      font-weight: bold;
    }
    .timestamp {
      font-size: 12px;
      color: #616161;
      text-align: right;
      margin-top: 15px;
      font-style: italic;
    }
  `;
  document.head.appendChild(style);
}

// Helper function to parse the email template format
function parseEmailTemplate(emailText) {
  const result = {
    audioModel: null,
    dataModel: null,
    chatModel: null,
    finalDecision: null,
    timestamp: null,
    user: null,
  };

  // Extracting Audio Model result
  const audioMatch = emailText.match(/Audio Model: (.*?)(?=\n|$)/);
  if (audioMatch) result.audioModel = audioMatch[1];

  // Extracting Data Model result
  const dataMatch = emailText.match(/Data Model: (.*?)(?=\n|$)/);
  if (dataMatch) {
    try {
      // Trying to parse as JSON
      const dataString = dataMatch[1];
      // Checking if it's array-like and parse it
      if (dataString.startsWith("[") && dataString.endsWith("]")) {
        result.dataModel = JSON.parse(dataString);
      } else {
        result.dataModel = dataString;
      }
    } catch (e) {
      // If parsing fails, use as string
      result.dataModel = dataMatch[1];
    }
  }

  // Extracting Chat Model result
  const chatMatch = emailText.match(/Chat Model: (.*?)(?=\n|$)/);
  if (chatMatch) result.chatModel = chatMatch[1];

  // Extracting timestamp
  const timeMatch = emailText.match(/Timestamp: (.*?)(?=\n|$)/);
  if (timeMatch) {
    try {
      const timestamp = new Date(timeMatch[1]);
      result.timestamp = timestamp.toLocaleString();
    } catch (e) {
      result.timestamp = timeMatch[1];
    }
  }

  // Extracting user
  const userMatch = emailText.match(/triggered by user: (.*?)(?=\n|$)/i);
  if (userMatch) result.user = userMatch[1];

  return result;
}

// Formatting data output for display
function formatDataOutput(dataModel) {
  if (!dataModel) return "No data available";

  // Handle array of prediction results
  if (Array.isArray(dataModel)) {
    return dataModel
      .map((item) => {
        if (typeof item.prediction === "object") {
          const pred = item.prediction;
          const stayProb = pred.stay_probability
            ? (pred.stay_probability * 100).toFixed(2) + "%"
            : "N/A";
          const churnProb = pred.churn_probability
            ? (pred.churn_probability * 100).toFixed(2) + "%"
            : "N/A";
          const finalPred = pred.prediction === 0 ? "STAY" : "CHURN";
          return `
          <div class="result-card">
            <div class="result-header">File: ${item.file}</div>
            <div class="result-body">
              <div><strong>Stay Probability:</strong> ${stayProb}</div>
              <div><strong>Churn Probability:</strong> ${churnProb}</div>
              <div><strong>Final Prediction:</strong> <span class="${
                finalPred === "STAY" ? "result-stay" : "result-churn"
              }">${finalPred}</span></div>
            </div>
          </div>
        `;
        } else {
          return `<div class="result-card">
          <div class="result-header">File: ${item.file}</div>
          <div class="result-body">${item.prediction}</div>
        </div>`;
        }
      })
      .join("");
  }

  // For non-array data
  return dataModel;
}

// Sending files to backend using Fetch API
function handleUpload() {
  showSpinner(); // show loading screen

  const formData = new FormData();

  // Adding all files with their categories
  for (const category in files) {
    files[category].forEach((file) => {
      formData.append(`${category}Files`, file);
    });
  }

  // Getting CSRF token from meta tag
  const csrfToken = document
    .querySelector('meta[name="csrf-token"]')
    ?.getAttribute("content");

  fetch("/upload", {
    method: "POST",
    body: formData,
    headers: {
      "X-CSRFToken": csrfToken || "",
    },
    credentials: "same-origin",
  })
    .then((response) => response.json())
    .then((data) => {
      console.log("Success:", data);

      hideSpinner();
      const result = data.result;

      showNotificationModal(result);
    })
    .catch((error) => {
      console.error("Error:", error);
      hideSpinner();
      alert("❌ Error uploading files!");
    });
}

// Handling OK button
document.getElementById("okButton").onclick = function () {
  document.getElementById("notificationModal").style.display = "none";
  // Remove result styles when modal is closed
  const resultStyles = document.getElementById("result-styles");
  if (resultStyles) resultStyles.remove();
};

// Handling notification close button
document.querySelector(".close-notification-button").onclick = function () {
  document.getElementById("notificationModal").style.display = "none";
  // Remove result styles when modal is closed
  const resultStyles = document.getElementById("result-styles");
  if (resultStyles) resultStyles.remove();
};

// Closing notification modal when clicking outside
window.addEventListener("click", function (event) {
  const modal = document.getElementById("notificationModal");

  // Only close if modal is visible and click is directly on the modal background
  if (modal.style.display === "flex" && event.target === modal) {
    modal.style.display = "none";
    // Remove result styles when modal is closed
    const resultStyles = document.getElementById("result-styles");
    if (resultStyles) resultStyles.remove();
  }
});
