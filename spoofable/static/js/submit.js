document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("analyzeForm");
    const submitButton = document.getElementById("submitButton");
    const spinner = document.getElementById("spinner");
    const urlInput = document.getElementById("url");

    form.addEventListener("submit", function (event) {
        const domainPattern =
            /^(?!:\/\/)([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$/;

        if (!domainPattern.test(urlInput.value.trim())) {
            alert("Please enter a valid domain.");
            event.preventDefault(); // Prevent form submission
            submitButton.disabled = false; // Re-enable the submit button
            spinner.style.display = "none"; // Hide the spinner
            return;
        }

        submitButton.disabled = true;
        spinner.style.display = "inline-block";
    });
});
