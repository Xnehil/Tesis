// static/js/utils.js
let fileCounter = 0; // Initialize a counter to ensure unique IDs

document.getElementById('archivo').addEventListener('change', function(event) {
  const files = event.target.files;
  const fileConfigs = document.getElementById('file-configurations');

  Array.from(files).forEach((file) => {
    const reader = new FileReader();
    const currentFileIndex = fileCounter++; // Use the counter to ensure unique IDs
    reader.onload = function(e) {
      const content = e.target.result;
      const lines = content.split(/\r\n|\r|\n/);
      const numLines = lines.length;
      const fileNameWithoutExtension = file.name.split('.').slice(0, -1).join('.');

      // Create card element
      const card = document.createElement('div');
      card.className = 'card mb-3';
      card.innerHTML = `
        <div class="card-header d-flex justify-content-between align-items-center" data-bs-toggle="collapse" data-bs-target="#collapse-${currentFileIndex}" aria-expanded="false" aria-controls="collapse-${currentFileIndex}" style="cursor: pointer;">
            <div>
                <h5 class="card-title mb-0">${file.name}</h5>
                <small class="text-muted">${numLines} ejemplos</small>
            </div>
            <div>
                <small class="text-muted" id="percentage-indicator-${currentFileIndex}">5% (${Math.ceil(0.05 * numLines)} líneas)</small>
            </div>
        </div>
        <div id="collapse-${currentFileIndex}" class="collapse">
            <div class="card-body">
                <div class="mb-2">
                <label for="example-lines-${currentFileIndex}" class="form-label mb-1">Ejemplo de líneas:</label>
                <pre class="bg-light p-2">${lines.slice(0, 2).join('\n')}</pre>
                </div>
                <div class="d-flex justify-content-between align-items-center mb-2">
                <div class="flex-grow-1 me-2">
                    <label for="model-name-${currentFileIndex}" class="form-label mb-1">Nombre del modelo:</label>
                    <input type="text" id="model-name-${currentFileIndex}" name="model_name_${currentFileIndex}" class="form-control form-control-sm" value="${fileNameWithoutExtension}" required>
                </div>
                <div class="flex-grow-1 ms-2">
                    <label for="percentage-${currentFileIndex}" class="form-label mb-1">Porcentaje de líneas a validar:</label>
                    <div class="d-flex align-items-center">
                        <input type="number" id="percentage-${currentFileIndex}" name="percentage_${currentFileIndex}" class="form-control form-control-sm me-2" min="0" max="100" value="5" step="0.1" required >
                        <small class="form-text text-muted" id="percentage-indicator-${currentFileIndex}">${numLines} líneas</small>
                    </div>
                </div>
                </div>
                <button type="button" class="btn btn-danger btn-sm" onclick="removeFile(this)">Eliminar</button>
            </div>
        </div>
      `;
      fileConfigs.appendChild(card);
      document.getElementById(`percentage-${currentFileIndex}`).addEventListener('input', function() {
        // Allow decimal points
        let percentage = this.value.replace(/[^0-9.,]/g, '');
        
        // Ensure the percentage remains within range and only has one decimal point
        if (percentage > 100) {
            percentage = 100;
        } else if (percentage.includes('.') && percentage.split('.')[1].length > 1) {
            percentage = parseFloat(percentage).toFixed(2); // Limit to one decimal
        }
        
        this.value = percentage;
        const linesToValidate = Math.ceil((percentage / 100) * numLines);
        document.getElementById(`percentage-indicator-${currentFileIndex}`).innerText = `${percentage}% (${linesToValidate} líneas)`;
      });

    };
    reader.readAsText(file);
  });
});

function removeFile(button) {
  const card = button.closest('.card');
  card.remove();
}