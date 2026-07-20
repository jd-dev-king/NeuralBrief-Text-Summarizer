"use strict";

/*
|--------------------------------------------------------------------------
| API Configuration
|--------------------------------------------------------------------------
|
| GitHub Pages can host only the frontend files. It cannot run Flask.
|
| After deploying the Flask backend, place its public URL below:
|
| const DEPLOYED_API_URL =
|     "https://your-neuralbrief-api.onrender.com";
|
*/

const LOCAL_API_URL = "http://127.0.0.1:5000";
const DEPLOYED_API_URL = "";

const isGitHubPages = window.location.hostname.endsWith("github.io");

const API_BASE_URL = isGitHubPages
    ? DEPLOYED_API_URL.replace(/\/$/, "")
    : LOCAL_API_URL;


/*
|--------------------------------------------------------------------------
| Interface Elements
|--------------------------------------------------------------------------
*/

const pasteModeButton = document.getElementById("pasteModeButton");
const uploadModeButton = document.getElementById("uploadModeButton");
const pastePanel = document.getElementById("pastePanel");
const uploadPanel = document.getElementById("uploadPanel");

const sourceText = document.getElementById("sourceText");
const sourceWordCount = document.getElementById("sourceWordCount");
const sourceCharacterCount = document.getElementById(
    "sourceCharacterCount"
);

const fileInput = document.getElementById("fileInput");
const browseButton = document.getElementById("browseButton");
const dropZone = document.getElementById("dropZone");

const selectedFileCard = document.getElementById(
    "selectedFileCard"
);

const selectedFileName = document.getElementById(
    "selectedFileName"
);

const selectedFileSize = document.getElementById(
    "selectedFileSize"
);

const removeFileButton = document.getElementById(
    "removeFileButton"
);

const ratioSlider = document.getElementById("ratioSlider");
const ratioOutput = document.getElementById("ratioOutput");

const summarizeButton = document.getElementById(
    "summarizeButton"
);

const clearButton = document.getElementById("clearButton");
const copyButton = document.getElementById("copyButton");

const downloadButton = document.getElementById(
    "downloadButton"
);

const inputMessage = document.getElementById("inputMessage");

const resultPlaceholder = document.getElementById(
    "resultPlaceholder"
);

const resultContent = document.getElementById("resultContent");
const summaryText = document.getElementById("summaryText");

const originalWordsStat = document.getElementById(
    "originalWordsStat"
);

const summaryWordsStat = document.getElementById(
    "summaryWordsStat"
);

const sentencesStat = document.getElementById(
    "sentencesStat"
);

const compressionStat = document.getElementById(
    "compressionStat"
);

const processingTimeStat = document.getElementById(
    "processingTimeStat"
);

const loadingOverlay = document.getElementById(
    "loadingOverlay"
);

const toast = document.getElementById("toast");
const statusDot = document.getElementById("statusDot");

const apiStatusText = document.getElementById(
    "apiStatusText"
);


/*
|--------------------------------------------------------------------------
| Application State
|--------------------------------------------------------------------------
*/

let activeMode = "paste";
let selectedFile = null;
let currentSummary = "";
let toastTimeout = null;
let apiAvailable = false;

const supportedExtensions = ["txt", "docx", "pdf"];
const maximumFileSize = 10 * 1024 * 1024;


/*
|--------------------------------------------------------------------------
| Input Mode
|--------------------------------------------------------------------------
*/

function setInputMode(mode) {
    activeMode = mode;

    const pasteActive = mode === "paste";

    pasteModeButton.classList.toggle(
        "active",
        pasteActive
    );

    uploadModeButton.classList.toggle(
        "active",
        !pasteActive
    );

    pastePanel.classList.toggle(
        "active",
        pasteActive
    );

    uploadPanel.classList.toggle(
        "active",
        !pasteActive
    );

    inputMessage.textContent = "";
}


/*
|--------------------------------------------------------------------------
| Text Statistics
|--------------------------------------------------------------------------
*/

function countWords(text) {
    const matches = text.trim().match(/\b[\w’'-]+\b/g);

    return matches ? matches.length : 0;
}

function updateTextCounters() {
    sourceWordCount.textContent = countWords(
        sourceText.value
    );

    sourceCharacterCount.textContent =
        sourceText.value.length;
}


/*
|--------------------------------------------------------------------------
| File Handling
|--------------------------------------------------------------------------
*/

function formatFileSize(bytes) {
    if (bytes < 1024) {
        return `${bytes} bytes`;
    }

    if (bytes < 1024 * 1024) {
        return `${(bytes / 1024).toFixed(1)} KB`;
    }

    return `${(bytes / (1024 * 1024)).toFixed(2)} MB`;
}

function getFileExtension(filename) {
    const sections = filename.split(".");

    if (sections.length < 2) {
        return "";
    }

    return sections.pop().toLowerCase();
}

function validateFile(file) {
    if (!file) {
        return "No file was selected.";
    }

    const extension = getFileExtension(file.name);

    if (!supportedExtensions.includes(extension)) {
        return "Please select a TXT, DOCX, or PDF document.";
    }

    if (file.size > maximumFileSize) {
        return "The selected file exceeds the 10 MB limit.";
    }

    return null;
}

function displaySelectedFile(file) {
    selectedFile = file;

    selectedFileName.textContent = file.name;
    selectedFileSize.textContent = formatFileSize(
        file.size
    );

    selectedFileCard.classList.remove("hidden");
    inputMessage.textContent = "";
}

function clearSelectedFile() {
    selectedFile = null;
    fileInput.value = "";

    selectedFileCard.classList.add("hidden");

    selectedFileName.textContent =
        "No file selected";

    selectedFileSize.textContent = "0 KB";
}

function handleFileSelection(file) {
    const validationError = validateFile(file);

    if (validationError) {
        showToast(validationError, "error");
        return;
    }

    displaySelectedFile(file);
}


/*
|--------------------------------------------------------------------------
| Loading and Notifications
|--------------------------------------------------------------------------
*/

function showLoading(isLoading) {
    loadingOverlay.classList.toggle(
        "hidden",
        !isLoading
    );

    summarizeButton.disabled =
        isLoading || !apiAvailable;
}

function showToast(message, type = "success") {
    if (toastTimeout) {
        window.clearTimeout(toastTimeout);
    }

    toast.textContent = message;
    toast.className = `toast visible ${type}`;

    toastTimeout = window.setTimeout(() => {
        toast.className = "toast";
    }, 3200);
}


/*
|--------------------------------------------------------------------------
| Results
|--------------------------------------------------------------------------
*/

function resetResults() {
    currentSummary = "";
    summaryText.textContent = "";

    resultPlaceholder.classList.remove("hidden");
    resultContent.classList.add("hidden");

    copyButton.disabled = true;
    downloadButton.disabled = true;

    originalWordsStat.textContent = "0";
    summaryWordsStat.textContent = "0";
    sentencesStat.textContent = "0 / 0";
    compressionStat.textContent = "0%";
    processingTimeStat.textContent = "0.000 sec";
}

function displayResults(responseData) {
    const statistics = responseData.statistics;

    currentSummary = responseData.summary;
    summaryText.textContent = responseData.summary;

    originalWordsStat.textContent =
        statistics.original_words.toLocaleString();

    summaryWordsStat.textContent =
        statistics.summary_words.toLocaleString();

    sentencesStat.textContent =
        `${statistics.summary_sentences} / ` +
        `${statistics.original_sentences}`;

    compressionStat.textContent =
        `${statistics.compression_percentage}%`;

    processingTimeStat.textContent =
        `${Number(
            statistics.processing_seconds
        ).toFixed(3)} sec`;

    resultPlaceholder.classList.add("hidden");
    resultContent.classList.remove("hidden");

    copyButton.disabled = false;
    downloadButton.disabled = false;
}


/*
|--------------------------------------------------------------------------
| API Responses
|--------------------------------------------------------------------------
*/

async function parseApiResponse(response) {
    let responseData;

    try {
        responseData = await response.json();
    } catch (error) {
        throw new Error(
            "The server returned an unreadable response."
        );
    }

    if (!response.ok || !responseData.success) {
        throw new Error(
            responseData.error ||
            "The summarization request failed."
        );
    }

    return responseData;
}

function ensureApiAvailable() {
    if (!API_BASE_URL || !apiAvailable) {
        throw new Error(
            "The live summarization API is not currently available."
        );
    }
}


/*
|--------------------------------------------------------------------------
| Text Summarization
|--------------------------------------------------------------------------
*/

async function summarizePastedText() {
    ensureApiAvailable();

    const text = sourceText.value.trim();

    if (!text) {
        throw new Error(
            "Paste an article or document before summarizing."
        );
    }

    if (countWords(text) < 50) {
        throw new Error(
            "Please provide at least 50 words."
        );
    }

    const response = await fetch(
        `${API_BASE_URL}/api/summarize`,
        {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                text,
                ratio:
                    Number(ratioSlider.value) / 100
            })
        }
    );

    return parseApiResponse(response);
}


/*
|--------------------------------------------------------------------------
| Document Summarization
|--------------------------------------------------------------------------
*/

async function summarizeUploadedFile() {
    ensureApiAvailable();

    if (!selectedFile) {
        throw new Error(
            "Select a TXT, DOCX, or PDF document first."
        );
    }

    const formData = new FormData();

    formData.append("file", selectedFile);

    formData.append(
        "ratio",
        Number(ratioSlider.value) / 100
    );

    const response = await fetch(
        `${API_BASE_URL}/api/upload`,
        {
            method: "POST",
            body: formData
        }
    );

    return parseApiResponse(response);
}


/*
|--------------------------------------------------------------------------
| Generate Summary
|--------------------------------------------------------------------------
*/

async function generateSummary() {
    inputMessage.textContent = "";

    if (!API_BASE_URL || !apiAvailable) {
        const message =
            "The summarization API has not been deployed yet.";

        inputMessage.textContent = message;
        showToast(message, "error");
        return;
    }

    showLoading(true);

    try {
        const responseData =
            activeMode === "paste"
                ? await summarizePastedText()
                : await summarizeUploadedFile();

        displayResults(responseData);

        showToast(
            "Summary generated successfully.",
            "success"
        );
    } catch (error) {
        const message =
            error instanceof Error
                ? error.message
                : "An unexpected error occurred.";

        inputMessage.textContent = message;
        showToast(message, "error");
    } finally {
        showLoading(false);
    }
}


/*
|--------------------------------------------------------------------------
| Copy and Download
|--------------------------------------------------------------------------
*/

async function copySummary() {
    if (!currentSummary) {
        return;
    }

    try {
        await navigator.clipboard.writeText(
            currentSummary
        );

        showToast(
            "Summary copied to the clipboard.",
            "success"
        );
    } catch (error) {
        const temporaryTextArea =
            document.createElement("textarea");

        temporaryTextArea.value = currentSummary;
        temporaryTextArea.style.position = "fixed";
        temporaryTextArea.style.opacity = "0";

        document.body.appendChild(
            temporaryTextArea
        );

        temporaryTextArea.select();
        document.execCommand("copy");
        temporaryTextArea.remove();

        showToast(
            "Summary copied to the clipboard.",
            "success"
        );
    }
}

function downloadSummary() {
    if (!currentSummary) {
        return;
    }

    const blob = new Blob(
        [currentSummary],
        {
            type: "text/plain;charset=utf-8"
        }
    );

    const downloadUrl =
        URL.createObjectURL(blob);

    const anchor =
        document.createElement("a");

    anchor.href = downloadUrl;

    anchor.download =
        "neuralbrief-summary.txt";

    document.body.appendChild(anchor);

    anchor.click();
    anchor.remove();

    URL.revokeObjectURL(downloadUrl);

    showToast(
        "Summary downloaded.",
        "success"
    );
}


/*
|--------------------------------------------------------------------------
| Clear Workspace
|--------------------------------------------------------------------------
*/

function clearApplication() {
    sourceText.value = "";
    updateTextCounters();

    clearSelectedFile();
    resetResults();

    inputMessage.textContent = "";

    ratioSlider.value = "20";
    ratioOutput.textContent = "20%";

    showToast(
        "Workspace cleared.",
        "success"
    );
}


/*
|--------------------------------------------------------------------------
| API Health
|--------------------------------------------------------------------------
*/

async function checkApiHealth() {
    if (!API_BASE_URL) {
        apiAvailable = false;

        statusDot.className =
            "status-dot status-offline";

        apiStatusText.textContent =
            "Demo Only";

        summarizeButton.disabled = true;

        inputMessage.textContent =
            "The live Flask API has not been deployed yet.";

        return;
    }

    statusDot.className =
        "status-dot status-checking";

    apiStatusText.textContent =
        "Checking...";

    try {
        const response = await fetch(
            `${API_BASE_URL}/api/health`,
            {
                method: "GET"
            }
        );

        const responseData =
            await parseApiResponse(response);

        if (responseData.status !== "online") {
            throw new Error(
                "The API is unavailable."
            );
        }

        apiAvailable = true;

        statusDot.className =
            "status-dot status-online";

        apiStatusText.textContent =
            "Online";

        summarizeButton.disabled = false;
        inputMessage.textContent = "";
    } catch (error) {
        apiAvailable = false;

        statusDot.className =
            "status-dot status-offline";

        apiStatusText.textContent =
            "Offline";

        summarizeButton.disabled = true;

        inputMessage.textContent =
            "The summarization API could not be reached.";
    }
}


/*
|--------------------------------------------------------------------------
| Event Listeners
|--------------------------------------------------------------------------
*/

pasteModeButton.addEventListener(
    "click",
    () => {
        setInputMode("paste");
    }
);

uploadModeButton.addEventListener(
    "click",
    () => {
        setInputMode("upload");
    }
);

sourceText.addEventListener(
    "input",
    updateTextCounters
);

ratioSlider.addEventListener(
    "input",
    () => {
        ratioOutput.textContent =
            `${ratioSlider.value}%`;
    }
);

browseButton.addEventListener(
    "click",
    (event) => {
        event.stopPropagation();
        fileInput.click();
    }
);

dropZone.addEventListener(
    "click",
    (event) => {
        if (event.target !== browseButton) {
            fileInput.click();
        }
    }
);

dropZone.addEventListener(
    "keydown",
    (event) => {
        if (
            event.key === "Enter" ||
            event.key === " "
        ) {
            event.preventDefault();
            fileInput.click();
        }
    }
);

fileInput.addEventListener(
    "change",
    () => {
        const [file] = fileInput.files;

        if (file) {
            handleFileSelection(file);
        }
    }
);

["dragenter", "dragover"].forEach(
    (eventName) => {
        dropZone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();

                dropZone.classList.add(
                    "dragging"
                );
            }
        );
    }
);

["dragleave", "drop"].forEach(
    (eventName) => {
        dropZone.addEventListener(
            eventName,
            (event) => {
                event.preventDefault();

                dropZone.classList.remove(
                    "dragging"
                );
            }
        );
    }
);

dropZone.addEventListener(
    "drop",
    (event) => {
        const [file] =
            event.dataTransfer.files;

        if (file) {
            handleFileSelection(file);
        }
    }
);

removeFileButton.addEventListener(
    "click",
    clearSelectedFile
);

summarizeButton.addEventListener(
    "click",
    generateSummary
);

clearButton.addEventListener(
    "click",
    clearApplication
);

copyButton.addEventListener(
    "click",
    copySummary
);

downloadButton.addEventListener(
    "click",
    downloadSummary
);


/*
|--------------------------------------------------------------------------
| Application Startup
|--------------------------------------------------------------------------
*/

updateTextCounters();
resetResults();
checkApiHealth();