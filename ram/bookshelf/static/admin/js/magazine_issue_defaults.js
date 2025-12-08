document.addEventListener('formset:added', function(event) {
  const newForm = event.target; // the new inline form element

  const defaultLanguage = document.querySelector('#id_language').value;
  const defaultStatus = document.querySelector('#id_published').checked;

  const languageInput = newForm.querySelector('select[name$="language"]');
  const statusInput = newForm.querySelector('input[name$="published"]');

  if (languageInput) {
      languageInput.value = defaultLanguage;
  }
  if (statusInput) {
    statusInput.checked = defaultStatus;
  }
});
