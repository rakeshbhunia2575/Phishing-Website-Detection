function toggleHistory() {
    const historyDiv = document.getElementById("historyBox");
    if (!historyDiv) return;

    if (historyDiv.style.display === "none") {
        historyDiv.style.display = "block";

        
        historyDiv.scrollIntoView({
            behavior: "smooth",
            block: "start"
        });
    } else {
        historyDiv.style.display = "none";
    }
}
