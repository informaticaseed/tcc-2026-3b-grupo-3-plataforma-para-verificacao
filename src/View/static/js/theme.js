(function () {
    const storageKey = "site-theme";
    const validThemes = ["original", "beige"];

    function applyTheme(theme) {
        const selectedTheme = validThemes.includes(theme) ? theme : "original";
        document.documentElement.dataset.theme = selectedTheme;

        const selectedControl = document.querySelector(`input[name="theme"][value="${selectedTheme}"]`);
        if (selectedControl) {
            selectedControl.checked = true;
        }
        return selectedTheme;
    }

    const savedTheme = localStorage.getItem(storageKey) || "beige";
    applyTheme(savedTheme);

    document.addEventListener("DOMContentLoaded", function () {
        applyTheme(savedTheme);
        document.querySelectorAll('input[name="theme"]').forEach(function (control) {
            control.addEventListener("change", function () {
                if (!control.checked) return;
                const selectedTheme = applyTheme(control.value);
                localStorage.setItem(storageKey, selectedTheme);
            });
        });
    });
})();
