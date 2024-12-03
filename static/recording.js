const recordButton = document.getElementById("recordButton");
const nameInput = document.getElementById("nameInput");
const statusText = document.getElementById("status");
const successContainer = document.getElementById("successContainer");
const editButtonContainer = document.getElementById("editButtonContainer");
const privateCheckbox = document.getElementById("private");

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

recordButton.addEventListener("click", async () => {
  if (!isRecording) {
    recordButton.textContent = "Stop Recording";
    statusText.textContent = "Recording...";
    isRecording = true;

    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
      audioChunks = [];

      const formData = new FormData();
      formData.append("audio", audioBlob);
      formData.append("name", nameInput.value);
      formData.append("private", privateCheckbox.checked); // Include checkbox value

      try {
        const response = await fetch(UPLOAD_URL, {
          method: "POST",
          body: formData,
        });

        if (response.ok) {
          const responseData = await response.json();
          statusText.textContent = "Audio uploaded successfully!";
          showSuccessButtons(responseData);
        } else {
          statusText.textContent = "Failed to upload audio.";
        }
      } catch (error) {
        statusText.textContent = "Error uploading audio.";
        console.error("Error uploading audio:", error);
      }
    };

    mediaRecorder.start();
  } else {
    recordButton.textContent = "Start Recording";
    statusText.textContent = "Processing...";
    isRecording = false;

    if (mediaRecorder) {
      mediaRecorder.stop();
    }
  }
});

function showSuccessButtons(responseData) {
  recordButton.style.display = "none";
  statusText.style.display = "none";

  successContainer.style.display = "block";

  const fileId = responseData.file_id;
  document.getElementById("fileListButton").onclick = () => window.location.href = `/user-files`;
  document.getElementById("editButton").onclick = () => window.location.href = `/edit-transcription/${fileId}`;
}
