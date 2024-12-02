// Log a message when the page loads
document.addEventListener("DOMContentLoaded", function () {
    console.log("Portfolio Insights Dashboard loaded successfully!");
});

// Highlight the active panel dynamically
function highlightActivePanel(panelId) {
    // Reset styles for all panels
    const panels = document.querySelectorAll(".panel");
    panels.forEach((panel) => {
        panel.style.border = "1px solid #ddd";
        panel.style.boxShadow = "none";
    });

    // Highlight the selected panel
    const activePanel = document.getElementById(panelId);
    if (activePanel) {
        activePanel.style.border = "2px solid #007BFF";
        activePanel.style.boxShadow = "0 0 10px rgba(0, 123, 255, 0.5)";
    }
}

// Attach click listeners to buttons for demonstration
document.addEventListener("click", function (event) {
    if (event.target.id === "search-button") {
        highlightActivePanel("right-pan");
        console.log("Search button clicked!");
    } else if (event.target.id === "confirm-button") {
        highlightActivePanel("right-pan");
        console.log("Confirm button clicked!");
    }
});

// Scroll smoothly to sections when certain actions are performed
function scrollToSection(sectionId) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.scrollIntoView({ behavior: "smooth" });
    }
}

// Example: Scroll to the "right-pan" when a button is clicked
document.addEventListener("click", function (event) {
    if (event.target.id === "add-row-button") {
        scrollToSection("right-pan");
    }
});
