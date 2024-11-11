document.addEventListener('DOMContentLoaded', function() {
    // Calculate progress (example calculation)
    var totalTasks = 100; // Replace with actual total tasks
    var completedTasks = 50; // Replace with actual completed tasks
    var progreso = 0;

    // Update progress bar
    var progressBar = document.getElementById('progress-bar');
    progressBar.style.width = progreso + '%';
    progressBar.setAttribute('aria-valuenow', progreso);
    progressBar.textContent = progreso.toFixed(2) + '%';

    if (progreso === 0) {
        document.querySelector('welcome-card').style.display = 'block';
    } else {
        document.querySelector('welcome-card').style.display = 'none';
    }
});

function showValidation() {
    document.querySelector('.container').style.display = 'none';
    document.getElementById('validation-template').style.display = 'block';
}

function saveProgress() {
    // Logic to save progress
    alert('Progreso guardado');
    window.location.reload();
}