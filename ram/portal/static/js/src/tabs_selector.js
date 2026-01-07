document.addEventListener("DOMContentLoaded", function () {
  // code to handle tab selection and URL hash synchronization
  const hash = window.location.hash.substring(1) // remove the '#' prefix
  if (hash) {
    const trigger = document.querySelector(`[data-bs-target="#nav-${hash}"]`);
    if (trigger) {
      bootstrap.Tab.getOrCreateInstance(trigger).show();
    }
  }
  //
  // update the URL hash when a tab is shown
  document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
    btn.addEventListener('shown.bs.tab', event => {
      const newHash = event.target.getAttribute('data-bs-target').replace('nav-', '');
      history.replaceState(null, null, newHash);
    });
  });

  // allow tab selection via a dropdown on small screens
  const selectElement = document.getElementById('tabSelector');
  if (!selectElement) return;
  selectElement.addEventListener('change', function () {
    const targetSelector = this.value;
    const triggerEl = document.querySelector(`[data-bs-target="#${targetSelector}"]`);
    if (triggerEl) {
      // Use Bootstrap 5.3's API — ensures transitions + ARIA updates
      const tabInstance = bootstrap.Tab.getOrCreateInstance(triggerEl);
      tabInstance.show();
    }
  });

  // keep the dropdown in sync if the user clicks a tab button
  document.querySelectorAll('[data-bs-toggle="tab"]').forEach(btn => {
    btn.addEventListener('shown.bs.tab', event => {
      const target = event.target.getAttribute('data-bs-target');
      selectElement.value = target.substring(1); // remove the '#' character
    });
  });
});
