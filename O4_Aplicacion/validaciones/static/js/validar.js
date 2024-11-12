let numValidacion = 0;
let totalValidaciones = 0;

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
        // document.querySelector('welcome-card').style.display = 'block';
        document.getElementById('welcome-card').style.display = 'block';
    } else {
        // document.querySelector('welcome-card').style.display = 'none';
        document.getElementById('welcome-card').style.display = 'none';
    }
    console.log(validador);
    totalValidaciones = validador.validaciones.length;
    updateEvaluation(validador.currentEvaluacion, validador.experimento.metricas);
});





function updateEvaluation(evaluacion, metricas) {
    const contenidoDiv = document.getElementById('contenido-evaluacion');
    const metricasDiv = document.getElementById('metricas-evaluacion');
    const botonesDiv = document.getElementById('botones-evaluacion');

    if (evaluacion) {
        contenidoDiv.innerHTML = evaluacion.ejemplo.contenido;
        botonesDiv.className = 'd-flex justify-content-between';
        botonesDiv.style.display = 'flex';

        // Make contenido-evaluacion blink
        // contenidoDiv.classList.add('blink');
    } else {
        contenidoDiv.innerHTML = '<p>Aquí verás el contenido de la evaluación. Tendrás que evaluarlo de acuerdo a las métricas que se te presentarán a tu derecha.</p>';
        botonesDiv.style.display = 'none';
    }

    let metricasHtml = '';
    metricas.forEach(metrica => {
        metricasHtml += `<div class="mb-2">
            <strong>${metrica.nombre}:</strong>
            <span data-bs-toggle="tooltip" title="${metrica.tooltip}"><i class="fas fa-info-circle"></i></span>
            <p>${metrica.descripcion}</p>`;
        if (metrica.tipoValor === 'bool') {
            metricasHtml += `<div>
                <label><input type="radio" name="metrica_${metrica.id}" value="sí"> Sí</label>
                <label><input type="radio" name="metrica_${metrica.id}" value="no"> No</label>
            </div>`;
        } else if (metrica.tipoValor === 'int' || metrica.tipoValor === 'float') {
            metricasHtml += `<div>
            <input type="range" name="metrica_${metrica.id}" min="${metrica.valorMin}" max="${metrica.valorMax}" step="${metrica.tipoValor === 'int' ? '1' : '0.1'}" value="${metrica.valorMin}" oninput="updateSliderValue(this)">
                <div class="d-flex justify-content-between mt-2">
                    <div class="badge bg-secondary">Valor actual: <span id="slider-value-${metrica.id}">${metrica.valorMin}</span></div>
                    <div class="text-muted">Mínimo: ${metrica.valorMin}, Máximo: ${metrica.valorMax}</div>
                </div>
            </div>`;
        }
        metricasHtml += `</div>`;
    });
    metricasDiv.innerHTML = metricasHtml;

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(tooltipTriggerEl => {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

function previousEvaluation() {
    if(numValidacion > 0){
        numValidacion--;
        let validacionActual = validador.validaciones[numValidacion];
        updateEvaluation(validacionActual, validador.experimento.metricas);
    } else {
        // Lanzar mensaje de que ya no hay más validaciones
    }
}

function nextEvaluation() {
    if(numValidacion < totalValidaciones){
        numValidacion++;
        let validacionActual = validador.validaciones[numValidacion];
        updateEvaluation(validacionActual, validador.experimento.metricas);
    } else {
        // Lanzar mensaje de que ya no hay más validaciones
    }
}

function updateSliderValue(slider) {
    const valueSpan = document.getElementById(`slider-value-${slider.name.split('_')[1]}`);
    valueSpan.textContent = slider.value;
}

function showValidation(){
    console.log('showValidation');
    // Esconer divs de bienvenida
    document.getElementById('welcome-card').style.display = 'none';
    document.getElementById('start-validation').style.display = 'none';
    document.getElementById('evaluation-instructions').style.display = 'none';

    numValidacion = 0;
    validacionActual = validador.validaciones[numValidacion];
    const totalValidaciones = validador.validaciones.length;
    updateEvaluation(validacionActual, validador.experimento.metricas);
}