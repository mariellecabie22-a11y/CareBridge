function confirmDelete() {
    return confirm("Are you sure you want to delete this discharge summary?");
}

// Live search
const searchInput = document.querySelector("#searchInput");

if (searchInput) {
    searchInput.addEventListener("keyup", function () {
        const filter = searchInput.value.toLowerCase();
        const cards = document.querySelectorAll(".patient-card");

        cards.forEach(card => {
            const text = card.innerText.toLowerCase();
            card.style.display = text.includes(filter) ? "block" : "none";
        });
    });
}

// Character counter
const textarea = document.querySelector("#summary");
const counter = document.querySelector("#counter");

if (textarea && counter) {
    textarea.addEventListener("input", () => {
        counter.textContent = textarea.value.length + " characters";
    });
}

// Print summary
function printSummary() {
    window.print();
}

// Format medications
function formatMedications() {
    const meds = document.querySelector("#medications");

    if (meds) {
        const lines = meds.value
            .split("\n")
            .filter(line => line.trim() !== "");

        meds.value = lines.map(line => "• " + line.replace(/^•\s*/, "")).join("\n");
    }
}

// Hamburger button
function toggleMenu() {
    const navLinks = document.querySelector("#navLinks");

    if (navLinks) {
        navLinks.classList.toggle("show");
    }
}

// show password option
function togglePassword() {
    const passwordInput = document.querySelector("#password");

    if (passwordInput.type === "password") {
        passwordInput.type = "text";
    } else {
        passwordInput.type = "password";
    }
}