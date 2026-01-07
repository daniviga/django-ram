// use Bootstrap 5's Tab component to manage tab navigation and synchronize with URL hash
document.addEventListener("DOMContentLoaded", function () {
  const selectElement = document.getElementById('tabSelector');
  // code to handle tab selection and URL hash synchronization
  const hash = window.location.hash.substring(1) // remove the '#' prefix
  if (hash) {
    const target = `#nav-${hash}`;
    const trigger = document.querySelector(`[data-bs-target="${target}"]`);
    if (trigger) {
      bootstrap.Tab.getOrCreateInstance(trigger).show();
      selectElement.value = target // keep the dropdown in sync
    }
  }

  // update the URL hash when a tab is shown
  document.querySelectorAll('button[data-bs-toggle="tab"]').forEach(btn => {
    btn.addEventListener('shown.bs.tab', event => {
      const newHash = event.target.getAttribute('data-bs-target').replace('nav-', '');
      history.replaceState(null, null, newHash);
    });
  });

  // allow tab selection via a dropdown on small screens
  if (!selectElement) return;
  selectElement.addEventListener('change', function () {
    const target = this.value;
    const trigger = document.querySelector(`[data-bs-target="${target}"]`);
    if (trigger) {
      const tabInstance = bootstrap.Tab.getOrCreateInstance(trigger);
      tabInstance.show();
    }
  });

  // keep the dropdown in sync if the user clicks a tab button
  document.querySelectorAll('[data-bs-toggle="tab"]').forEach(btn => {
    btn.addEventListener('shown.bs.tab', event => {
      const target = event.target.getAttribute('data-bs-target');
      selectElement.value = target
    });
  });
});
