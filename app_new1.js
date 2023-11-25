document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();

    var formData = new FormData();
    formData.append('video', document.getElementById('fileInput').files[0]);

    fetch('/api/load_video', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const videoId = data.id;
        checkVideoStatus(videoId);
        addVideoRow(videoId);
    })
    .catch(error => console.error('Error:', error));
});

function addVideoRow(videoId) {
    const tableBody = document.getElementById('videoInfo');
    const row = tableBody.insertRow();
    row.id = `video-${videoId}`;
    row.innerHTML = `
        <td>${videoId}</td>
        <td id="class-${videoId}">Pending</td>
        <td id="probability-${videoId}">Pending</td>
        <td id="fccCode-${videoId}">Pending</td>
    `;
}

function checkVideoStatus(videoId) {
    fetch('/api/get_video_status', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === '2') {
            getVideoParams(videoId);
        } else {
            setTimeout(() => checkVideoStatus(videoId), 5000); // Check again after 5 seconds
        }
    })
    .catch(error => console.error('Error:', error));
}

function getVideoParams(videoId) {
    fetch('/api/video_params', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ video_id: videoId })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById(`class-${videoId}`).textContent = data.class_pred;
        document.getElementById(`probability-${videoId}`).textContent = data.probability;
        document.getElementById(`fccCode-${videoId}`).textContent = data.special_code;
    })
    .catch(error => console.error('Error:', error));
}
