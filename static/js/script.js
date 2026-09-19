function toggleHistory() {
    const historyDiv = document.getElementById("historyBox");
    const toggleButton = document.querySelector(".toggle-btn");
    if (!historyDiv) return;

    if (historyDiv.style.display === "none") {
        historyDiv.style.display = "block";
        if (toggleButton) toggleButton.setAttribute("aria-expanded", "true");

        //  Smooth scroll to history top
        historyDiv.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    } else {
        historyDiv.style.display = "none";
        if (toggleButton) toggleButton.setAttribute("aria-expanded", "false");
    }
}
