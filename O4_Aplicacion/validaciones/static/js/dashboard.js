

document.addEventListener('DOMContentLoaded', function() {
    // Function to calculate and update the progress
    function updateProgress() {
        const validadores = window.experimento.validadores;
        const totalValidadores = validadores.length;
        let completedValidadores = 0;

        validadores.forEach(validador => {
            // Assuming each validador has a 'completed' property indicating their progress
            if (validador.completed) {
                completedValidadores++;
            }
        });

        const progress = (completedValidadores / totalValidadores) * 100;
        const progressBar = document.getElementById('progress-bar');
        progressBar.style.width = `${progress}%`;
        progressBar.setAttribute('aria-valuenow', progress);
        progressBar.textContent = `${progress.toFixed(2)}%`;
    }

    // Call the function to update the progress
    console.log(window.experimento);
    updateProgress();

    for (let validador of window.experimento.validadores) {
        validador.progress = calculateProgress(); // Replace with your actual calculation logic
        const progressBar = document.getElementById(`progress-bar-${validador.id}`);
        progressBar.style.width = `${validador.progress}%`;
        progressBar.setAttribute('aria-valuenow', validador.progress);
        progressBar.textContent = `${validador.progress}%`;
    }
});

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(function() {
        alert('URL copied to clipboard');
    }, function(err) {
        console.error('Could not copy text: ', err);
    });
}



function calculateProgress() {
    // Replace this with your actual logic to calculate progress
    return 50; // Example progress value
}
