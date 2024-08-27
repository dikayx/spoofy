document.querySelectorAll(".toggle-icon").forEach((button) => {
    button.addEventListener("click", function () {
        const icon = this.querySelector("i");
        icon.classList.toggle("bi-chevron-down");
        icon.classList.toggle("bi-chevron-up");
    });
});
