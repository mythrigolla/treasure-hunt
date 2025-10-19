// This script will show immediate feedback before form submission (optional)
document.addEventListener("DOMContentLoaded", function() {
    const form = document.querySelector("form");
    const feedback = document.querySelector("h3");

    form.addEventListener("submit", function(event) {
        const selected = document.querySelector("input[name='option']:checked");
        if (!selected) {
            event.preventDefault();
            alert("Please select an option!");
            return;
        }

        // Optional: you can show temporary message before page reload
        feedback.textContent = "Checking your answer...";
    });
});
