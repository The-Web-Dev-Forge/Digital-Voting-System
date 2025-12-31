const video = document.getElementById('video')

Promise.all([
    faceapi.nets.tinyFaceDetector.loadFromUri('/Face_Detection_javaScript/models'),
    faceapi.nets.faceLandmark68Net.loadFromUri('/Face_Detection_javaScript/models'),
    faceapi.nets.faceRecognitionNet.loadFromUri('/Face_Detection_javaScript/models'),
    faceapi.nets.faceExpressionNet.loadFromUri('/Face_Detection_javaScript/models')
]).then(startVideo)

function startVideo() {
  navigator.getUserMedia(
    { video: {} },
    stream => video.srcObject = stream,
    err => console.error(err)
  )
}

video.addEventListener('play', () => {
    const canvas = faceapi.createCanvasFromMedia(video)
    document.body.append(canvas)
    const displaySize = { width: video.width, height: video.height }
    faceapi.matchDimensions(canvas, displaySize)
  
    let faceDetected = false;
    const detectionInterval = 100; // Interval to check for face detection (in ms)
    const timeout = 10000; // 10 seconds timeout
  
    const intervalId = setInterval(async () => {
      const d2 = await faceapi.detectSingleFace(video, new faceapi.TinyFaceDetectorOptions())
      if (d2) {
        faceDetected = true;
        clearInterval(intervalId);
        console.log("Face detected");
        window.location.href = "/face-detection-success";
      }
      const resizedDetections = faceapi.resizeResults(detections, displaySize)
      canvas.getContext('2d').clearRect(0, 0, canvas.width, canvas.height)
      faceapi.draw.drawDetections(canvas, resizedDetections)
      faceapi.draw.drawFaceLandmarks(canvas, resizedDetections)
      faceapi.draw.drawFaceExpressions(canvas, resizedDetections)
    }, detectionInterval);
  
    setTimeout(() => {
      if (!faceDetected) {
        clearInterval(intervalId);
        console.log("No face detected");
        alert("No face detected within 10 seconds. Redirecting to homepage.");
        window.location.href = "/unauthorized";
      }
    }, timeout);
  })
