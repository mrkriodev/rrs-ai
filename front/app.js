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
    })
    .catch(error => console.error('Error:', error));
});

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
        if (data.status === 'done') {
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
        document.getElementById('quality').textContent = data.quality;
        document.getElementById('contentType').textContent = data.content_type;
        document.getElementById('length').textContent = data.length;
        document.getElementById('statusWindow').style.display = 'block';
    })
    .catch(error => console.error('Error:', error));
}
