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
        updateProgressText();
        mostrarMensajeFinal();
    } else {
        let validacionActual = null 
        if (numValidacion >= 0 && numValidacion < totalValidaciones) {
            validacionActual = validador.validaciones[numValidacion];
            showValidation(numValidacion);
        }
        updateEvaluation(validacionActual, validador.experimento.metricas);
        updateProgressText();
    }
});

function actualizarProgreso(progreso) {
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
}

function calcularProgreso() {
    // Calculate progress (example calculation)
    let completado = validador.validaciones.filter(validacion => validacion.terminado).length;
    let progreso = completado / validador.validaciones.length * 100;
    return progreso;
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
    metricas.forEach(metrica => {
        // const puntuacion = evaluacion.puntuaciones.find(puntuacion => puntuacion.metrica === metrica.id);
        // const valor = puntuacion ? puntuacion.valor : metrica.valorMin;
        let valor = '';
        if (evaluacion) {
            const puntuacion = evaluacion.puntuaciones.find(puntuacion => puntuacion.metrica_id === metrica.id);
            valor = puntuacion ? puntuacion.valor : metrica.valorMin;
            // Convertir null a ''  
            if (valor === null) {
                valor = '';
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
    updateProgressText();
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
        let validacionActual = validador.validaciones[numValidacion];
        updateEvaluation(validacionActual, validador.experimento.metricas);
    } else {
        // Lanzar mensaje de que ya no hay más validaciones
        alert("Esta es la primera validación.");
    }
}

function nextEvaluation() {
    if (areAllMetricsCompleted()) {
        if (numValidacion + 1 < totalValidaciones) {
            guardarPuntuaciones();
            numValidacion++;
            let validacionActual = validador.validaciones[numValidacion];
            updateEvaluation(validacionActual, validador.experimento.metricas);
        } else {
            guardarPuntuaciones();
            updateProgressText();
            mostrarMensajeFinal();
        }
    } else {
        // Lanzar mensaje de que todas las métricas deben ser completadas
        alert("Por favor, complete todas las métricas antes de continuar.");
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
        // Enviar validacion actualizada al servidor
        fetch(`/api/validacion/${validacionActual.id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(validacionActual)
        })
        .then(response => response.json())
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

function updateProgressText() {
    const progressText = document.getElementById('progress-text');
    progressText.textContent = `${numValidacion + 1} de ${totalValidaciones}`;

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
    updateEvaluation(validacionActual, validador.experimento.metricas);
}
