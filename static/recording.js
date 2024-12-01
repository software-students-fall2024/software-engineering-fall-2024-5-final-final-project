const recordButton = document.getElementById("recordButton");
const nameInput = document.getElementById("nameInput");
const statusText = document.getElementById("status");

let mediaRecorder;
let audioChunks = [];
let isRecording = false;

recordButton.addEventListener("click", async () => {
  if (!isRecording) {
    recordButton.textContent = "Stop Recording";
    statusText.textContent = "Recording...";
    isRecording = true;

    // Get the audio stream
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    // Push binary data chunks to `audioChunks` array
    mediaRecorder.ondataavailable = (event) => {
      audioChunks.push(event.data);
    };

    // When recording stops, process the binary data
    mediaRecorder.onstop = async () => {
      const audioBlob = new Blob(audioChunks, { type: mediaRecorder.mimeType }); // Use native mimeType
      console.log(mediaRecorder.mimeType);
      audioChunks = []; // Clear chunks

      // Send the binary data to the server
      const formData = new FormData();
      formData.append("audio", audioBlob); // Raw binary audio data
      formData.append("name", nameInput.value);

      try {
        const response = await fetch(UPLOAD_URL, {
          method: "POST",
          body: formData,
        });
        if (response.ok) {
          statusText.textContent = "Audio uploaded successfully!";
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

    // Stop recording
    if (mediaRecorder) {
      mediaRecorder.stop();
    }
  }
});
