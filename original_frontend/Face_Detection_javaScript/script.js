const video = document.getElementById('video');

Promise.all([
  faceapi.nets.tinyFaceDetector.loadFromUri('/Face_Detection_javaScript/models'),
  faceapi.nets.faceLandmark68Net.loadFromUri('/Face_Detection_javaScript/models'),
  faceapi.nets.faceRecognitionNet.loadFromUri('/Face_Detection_javaScript/models'),
  faceapi.nets.faceExpressionNet.loadFromUri('/Face_Detection_javaScript/models')
]).then(startVideo);

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    stream => video.srcObject = stream,
    err => console.error(err)
  );
}

video.addEventListener('play', () => {
  const canvas = faceapi.createCanvasFromMedia(video);
  document.body.append(canvas);
  const displaySize = { width: video.width, height: video.height };
  faceapi.matchDimensions(canvas, displaySize);

  let faceDetected = false;
  const intervalId = setInterval(async () => {
    const detected = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions());
    if (detected) {
      console.log("Face detected");
      faceDetected = true;
      clearInterval(intervalId);

      // Wait for 10 seconds
      setTimeout(() => {
        fetch('/face-detection-status', {
          method: 'POST',
          body: JSON.stringify({ faceDetected: true }),
          headers: { 'Content-Type': 'application/json' }
        });
      }, 10000); // 10 seconds
    } else {
      console.log("Face not detected");
      fetch('/face-detection-status', {
        method: 'POST',
        body: JSON.stringify({ faceDetected: false }),
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }, 1000); // Check every second
});

