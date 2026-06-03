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
    if (window.innerWidth <= 760) {
        alert("On mobile, use your browser menu and choose Share or Print.");
    } else {
        window.print();
    }
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

// Show password and confirm password
function togglePassword() {
    const passwordInput = document.querySelector("#password");
    const newPasswordInput = document.querySelector("#new_password");
    const confirmPasswordInput = document.querySelector("#confirm_password");

    const fields = [
        passwordInput,
        newPasswordInput,
        confirmPasswordInput
    ];

    fields.forEach(field => {
        if (field) {
            field.type = field.type === "password"
                ? "text"
                : "password";
        }
    });
}