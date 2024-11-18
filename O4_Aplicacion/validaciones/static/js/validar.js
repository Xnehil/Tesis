let numValidacion = 0;
let totalValidaciones = 0;

document.addEventListener('DOMContentLoaded', function() {
    // Calculate progress (example calculation)
    let progreso = calcularProgreso();
    actualizarProgreso(progreso);

    // Calcular primera evaluación sin terminar
    let todosTerminados = true;
    for (let i = 0; i < validador.validaciones.length; i++) {
        if (!validador.validaciones[i].terminado) {
            numValidacion = i;
            todosTerminados = false;
            console.log("numValidacion: " + numValidacion);
            break;
        }
    }
    console.log(validador);
    totalValidaciones = validador.validaciones.length;
    if (todosTerminados) {
        numValidacion = totalValidaciones;
        document.getElementById('welcome-card').style.display = 'none';
        document.getElementById('start-validation').style.display = 'none';
        document.getElementById('evaluation-instructions').style.display = 'none';
        updateProgressText(progreso);
        mostrarMensajeFinal();
    } else {
        let validacionActual = null 
        if (numValidacion > 0 && numValidacion < totalValidaciones) {
            validacionActual = validador.validaciones[numValidacion];
            showValidation(numValidacion);
        }
        updateEvaluation(validacionActual, validador.experimento.metricas);
        updateProgressText(progreso);
    }
});

function actualizarProgreso(progreso) {
    // Update progress bar
    console.log('Actualizando progreso: ' + progreso);
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
}

function calcularProgreso() {
    // Calculate progress (example calculation)
    let completado = validador.validaciones.filter(validacion => validacion.terminado).length;
    let progreso = completado / validador.validaciones.length * 100;
    return progreso;
}

function actualizarProgresoBarraYTexto(final=false) {
    let progreso = calcularProgreso();
    actualizarProgreso(progreso);
    updateProgressText(progreso);
}



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
    if (!evaluacion) {
        metricasHtml = '<p>Así se verán las métricas de la evaluación. Tendrás que completarlas todas antes de continuar.</p>';
    }
    metricas.forEach(metrica => {
        // const puntuacion = evaluacion.puntuaciones.find(puntuacion => puntuacion.metrica === metrica.id);
        // const valor = puntuacion ? puntuacion.valor : metrica.valorMin;
        let valor = '';
        if (evaluacion) {
            const puntuacion = evaluacion.puntuaciones.find(puntuacion => puntuacion.metrica_id === metrica.id);
            valor = puntuacion ? puntuacion.valor : metrica.valorMin;
            // Convertir null a ''  
            if (valor === null) {
                valor = metrica.valorMin;
            }
        } 

        metricasHtml += `<div class="mb-2">
                <strong>${metrica.nombre}:</strong>
                <span data-bs-toggle="tooltip" title="${metrica.tooltip}"><i class="fas fa-info-circle"></i></span>
                <p>${metrica.descripcion}</p>`;
            if (metrica.tipoValor === 'bool') {
                metricasHtml += `<div>
                    <label><input type="radio" name="metrica_${metrica.id}" value="True" ${valor === 'True' ? 'checked' : ''}> Sí</label>
                    <label><input type="radio" name="metrica_${metrica.id}" value="False" ${valor === 'False' ? 'checked' : ''}> No</label>
                </div>`;
            } else if (metrica.tipoValor === 'int' || metrica.tipoValor === 'float') {
                metricasHtml += `<div>
                    <input type="range" name="metrica_${metrica.id}" min="${metrica.valorMin}" max="${metrica.valorMax}" step="${metrica.tipoValor === 'int' ? '1' : '0.1'}" value="${valor}" oninput="updateSliderValue(this)">
                    <div class="d-flex justify-content-between mt-2">
                        <div class="badge bg-secondary">Valor actual: <span id="slider-value-${metrica.id}">${valor}</span></div>
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
        if (areAllMetricsCompleted()) {
            guardarPuntuaciones();
        }
        numValidacion--;
        actualizarProgresoBarraYTexto();
        let validacionActual = validador.validaciones[numValidacion];
        updateEvaluation(validacionActual, validador.experimento.metricas);
    } else {
        showAlert("Esta es la primera validación.");
    }
}

function nextEvaluation() {
    if (areAllMetricsCompleted()) {
        if (numValidacion + 1 < totalValidaciones) {
            guardarPuntuaciones();
            numValidacion++;
            let validacionActual = validador.validaciones[numValidacion];
            actualizarProgresoBarraYTexto();
            updateEvaluation(validacionActual, validador.experimento.metricas);
        } else {
            guardarPuntuaciones();
            actualizarProgresoBarraYTexto(final=true);
            mostrarMensajeFinal();
        }
    } else {
        // Lanzar mensaje de que todas las métricas deben ser completadas
        showAlert("Por favor, complete todas las métricas antes de continuar.");
    }
}

function updateSliderValue(slider) {
    const valueSpan = document.getElementById(`slider-value-${slider.name.split('_')[1]}`);
    valueSpan.textContent = slider.value;
}

function showValidation(anteriorNumValidacion) {
    console.log('showValidation');
    // Esconer divs de bienvenida
    document.getElementById('welcome-card').style.display = 'none';
    document.getElementById('start-validation').style.display = 'none';
    document.getElementById('evaluation-instructions').style.display = 'none';

    numValidacion = anteriorNumValidacion ? anteriorNumValidacion : 0;
    validacionActual = validador.validaciones[numValidacion];
    updateEvaluation(validacionActual, validador.experimento.metricas);
}

function guardarPuntuaciones(){
    // console.log('guardarPuntuaciones');
    let metricas = validador.experimento.metricas;
    let puntuaciones = [];
    metricas.forEach(metrica => {
        let valor = '';
        if (metrica.tipoValor === 'bool') {
            valor = document.querySelector(`input[name="metrica_${metrica.id}"]:checked`).value;
        } else if (metrica.tipoValor === 'int' || metrica.tipoValor === 'float') {
            valor = document.querySelector(`input[name="metrica_${metrica.id}"]`).value;
        }
        puntuaciones.push({
            metrica: metrica.id,
            valor: valor
        });
    });
    // console.log(puntuaciones);
    // Enviar puntuaciones al servidor
    
    // Crear cuerpo para el put
    let validacionActual = validador.validaciones[numValidacion];
    let hasChanges = false;

    for (let i = 0; i < puntuaciones.length; i++) {
        if (validacionActual.puntuaciones[i].valor !== puntuaciones[i].valor) {
            validacionActual.puntuaciones[i].valor = puntuaciones[i].valor;
            hasChanges = true;
        }
    }
    if (hasChanges) {
        validacionActual.terminado = true;
        showLoadingOverlay();
        // Enviar validacion actualizada al servidor
        fetch(`/api/validacion/${validacionActual.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(validacionActual)
        })
        .then(response => response.json())
        .then(() => {
            hideLoadingOverlay();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    } else {
        console.log('No hay cambios');
    }
}

function areAllMetricsCompleted() {
    const metricas = document.querySelectorAll('[name^="metrica_"]');
    for (let metrica of metricas) {
        if (metrica.type === 'radio') {
            const radios = document.querySelectorAll(`[name="${metrica.name}"]`);
            if (![...radios].some(radio => radio.checked)) {
                return false;
            }
        } else if (metrica.type === 'range') {
            if (metrica.value === '') {
                return false;
            }
        }
    }
    return true;
}

function updateProgressText(progreso) {
    const progressText = document.getElementById('progress-text');
    console.log('updateProgressText');
    if (progreso === 100) {
        progressText.textContent = `Todas las validaciones completadas`;
    } else {
        console.log(progreso);
        let completadas = Math.floor(progreso * totalValidaciones / 100);
        progressText.textContent = `${completadas} de ${totalValidaciones}`;
    }

    const progressText2 = document.getElementById('titulo-numero-ejemplo');
    if (numValidacion === totalValidaciones) {
        // Ocultar progressText2
        progressText2.textContent = '';
    } else{
        progressText2.textContent = `Viendo ejemplo ${numValidacion + 1} de ${totalValidaciones}`;
    }
    
}

function mostrarMensajeFinal() {
    const evaluacionContenidoDiv = document.getElementById('evaluacion-contenido');
    const botonesDiv = document.getElementById('botones-evaluacion');

    evaluacionContenidoDiv.style.display = 'none';
    botonesDiv.oldHTML = botonesDiv.innerHTML;
    botonesDiv.className = 'd-flex justify-content-center';
    botonesDiv.innerHTML = '<button class="btn btn-primary btn-lg w-50" onclick="volverUltimaValidacion()">Volver a la última validación</button>';
    
    const mensajeFinalDiv = document.createElement('div');
    mensajeFinalDiv.className = 'alert alert-info text-center mt-4 mb-4 pt-4 pb-2';
    mensajeFinalDiv.innerHTML = '<h3>Gracias por completar las validaciones.</h3><p>Has completado todas las validaciones. Puedes volver a revisar las validaciones anteriores si lo deseas.</p>';
    mensajeFinalDiv.id = 'mensaje-final';
    evaluacionContenidoDiv.parentNode.insertBefore(mensajeFinalDiv, evaluacionContenidoDiv.nextSibling);
}

function volverUltimaValidacion() {
    const evaluacionContenidoDiv = document.getElementById('evaluacion-contenido');
    const mensajeFinalDiv = document.getElementById('mensaje-final');
    const botonesDiv = document.getElementById('botones-evaluacion');

    evaluacionContenidoDiv.style.display = '';
    mensajeFinalDiv.remove();

    numValidacion = totalValidaciones - 1;
    // console.log("numValidacion: " + numValidacion);
    botonesDiv.innerHTML = botonesDiv.oldHTML;
    let validacionActual = validador.validaciones[numValidacion];
    updateProgressText(calcularProgreso());
    updateEvaluation(validacionActual, validador.experimento.metricas);
}

function showAlert(message) {
    // Remove existing alert if any
    const existingAlert = document.getElementById('custom-alert');
    if (existingAlert) {
        existingAlert.remove();
    }

    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.id = 'custom-alert';
    alertDiv.className = 'alert alert-secondary alert-dismissible fade show';
    alertDiv.role = 'alert';
    alertDiv.style.position = 'fixed';
    alertDiv.style.top = '50%';
    alertDiv.style.left = '50%';
    alertDiv.style.transform = 'translate(-50%, -50%)';
    alertDiv.style.zIndex = '1050'; // Ensure it appears above other elements
    alertDiv.style.padding = '1.5rem';
    alertDiv.style.borderRadius = '10px';
    alertDiv.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
    alertDiv.style.backdropFilter = 'blur(10px)';
    alertDiv.innerHTML = `
        <div style="padding-right: 30px;">
            ${message}
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="position: absolute; top: 10px; right: 10px;"></button>
    `;

    // Insert alert into the DOM
    document.body.appendChild(alertDiv);

    // Automatically remove the alert after a few seconds
    setTimeout(() => {
        alertDiv.classList.remove('show');
        alertDiv.classList.add('fade');
        setTimeout(() => alertDiv.remove(), 150);
    }, 4000);
}

function showLoadingOverlay() {
    const overlay = document.createElement('div');
    overlay.id = 'loading-overlay';
    overlay.style.position = 'fixed';
    overlay.style.top = '0';
    overlay.style.left = '0';
    overlay.style.width = '100%';
    overlay.style.height = '100%';
    overlay.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
    overlay.style.zIndex = '9999';
    overlay.style.display = 'flex';
    overlay.style.justifyContent = 'center';
    overlay.style.alignItems = 'center';
    overlay.innerHTML = '<i class="fas fa-spinner fa-spin fa-3x text-primary"></i>';
    document.body.appendChild(overlay);
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.remove();
    }
}