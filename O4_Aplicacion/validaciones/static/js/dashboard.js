

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

    const toastElList = document.querySelectorAll('.toast')
    const toastList = [...toastElList].map(toastEl => new bootstrap.Toast(toastEl, option))
});

function copyToClipboard(text) {
    // Seleccionar todo el texto antes del primer / de la ruta actual
    const baseUrl = `${window.location.protocol}//${window.location.host}`;
    // Construct the full URL
    const fullUrl = `${baseUrl}/validar/${text}`;

    navigator.clipboard.writeText(fullUrl).then(function() {
        showToast('URL copiada al portapapeles', 'black');
    }, function(err) {
        showToast('No se pudo copiar el texto: ' + err, 'danger');
    });
}

function showToast(message, type) {
    const toastContainer = document.getElementById('toast-container');
    const toastId = 'toast-' + Date.now();
    const toastHtml = `
        <div id="${toastId}" class="toast" role="alert" aria-live="assertive" aria-atomic="true" data-bs-autohide="true" data-bs-delay="1500">
            <div class="toast-body bg-success bg-opacity-75 text-white">
                ${message}
            </div>
        </div>
    `;
    toastContainer.insertAdjacentHTML('beforeend', toastHtml);
    
    const toastElement = document.getElementById(toastId);
    const toast = new bootstrap.Toast(toastElement);
    toast.show();

    toastElement.addEventListener('hidden.bs.toast', function () {
        toastElement.remove();
    });
}

function submitForm(event, validadorId) {
    event.preventDefault();
    const form = document.getElementById(`validador-form-${validadorId}`);
    const formData = new FormData(form);
    const data = {};
    formData.forEach((value, key) => {
        data[key] = value;
    });

    fetch(`/api/validador/${validadorId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        console.log('Success:', data);
    })
    .then(() => {
        updateSpan(validadorId, data.nombre);
    })
    .catch((error) => {
        console.error('Error:', error);
    });

}

function updateSpan(validadorId, newValue) {
    const span = document.getElementById(`validador-span-${validadorId}`);
    const tipo = span.textContent.split(' - ')[0]; // Extract the type (Experto/Nativo)
    span.textContent = `${tipo} - ${newValue || 'Sin nombre'}`;
}

function calculateProgress() {
    // Replace this with your actual logic to calculate progress
    return 50; // Example progress value
}
