document.addEventListener("DOMContentLoaded", function () {
    const accordionItems = document.querySelectorAll(".accordion-item");
    const validacionItem = document.querySelector('#headingValidacion').closest('.accordion-item');
    const numNativeInput = validacionItem.querySelector('#num-native');
    const numExpertsInput = validacionItem.querySelector('#num-experts');
    const checkboxes = validacionItem.querySelectorAll('input[type="checkbox"]');

    function checkCompletion() {
      let allFilled = true;
      let atLeastOneChecked = false;

      if (!numNativeInput.value || !numExpertsInput.value) {
        allFilled = false;
      }

      checkboxes.forEach((checkbox) => {
        if (checkbox.checked) {
          atLeastOneChecked = true;
        }
      });

      if (allFilled && atLeastOneChecked) {
        validacionItem.setAttribute("data-completed", "true");
        // validacionItem.querySelector('.completed-icon').style.display = 'inline';
      } else {
        validacionItem.setAttribute("data-completed", "false");
        // validacionItem.querySelector('.completed-icon').style.display = 'none';
      }
    }

    if (numNativeInput && numExpertsInput) {
      numNativeInput.addEventListener('input', checkCompletion);
      numExpertsInput.addEventListener('input', checkCompletion);
    }

    checkboxes.forEach((checkbox) => {
      checkbox.addEventListener('change', checkCompletion);
    });

    accordionItems.forEach((item) => {
      if (item === validacionItem) return;

      const inputs = item.querySelectorAll("input, textarea, select");
      inputs.forEach((input) => {
        input.addEventListener("change", function () {
          let allFilled = true;
          inputs.forEach((input) => {
            if (!input.value) {
              allFilled = false;
            }
          });
          if (allFilled) {
            item.setAttribute("data-completed", "true");
          } else {
            item.setAttribute("data-completed", "false");
          }
        });
      });
    });
  });