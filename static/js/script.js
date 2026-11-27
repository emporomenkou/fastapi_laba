document.addEventListener("DOMContentLoaded", () => {
    // 1. Ползунок возраста без стрелочек клавиатуры
    const ageSlider = document.getElementById("age-slider");
    const ageDisplay = document.getElementById("age-display");

    if (ageSlider && ageDisplay) {
        ageSlider.addEventListener("keydown", (e) => {
            if (["ArrowLeft", "ArrowRight", "ArrowUp", "ArrowDown"].includes(e.key)) {
                e.preventDefault();
            }
        });

        ageSlider.addEventListener("input", () => {
            ageDisplay.textContent = parseFloat(ageSlider.value).toFixed(2);
        });
    }

    // 2. Проверка HEX-кода цвета
    const targetBox = document.getElementById("target-color");
    const userBox = document.getElementById("user-color");
    const hexInput = document.getElementById("hex-input");

    if (targetBox && userBox && hexInput) {
        targetBox.style.backgroundColor = targetBox.dataset.hex || "#3A5FCD";

        hexInput.addEventListener("input", () => {
            const val = hexInput.value.trim();
            if (/^#[0-9A-Fa-f]{6}$/.test(val)) {
                userBox.style.backgroundColor = val;
            }
        });
    }

    // 3. Разблокировка галочки только после прокрутки соглашения до низа
    const tosBox = document.getElementById("tos-box");
    const tosCheckbox = document.getElementById("tos-checkbox");

    if (tosBox && tosCheckbox) {
        tosBox.addEventListener("scroll", () => {
            const isAtBottom = tosBox.scrollHeight - tosBox.scrollTop <= tosBox.clientHeight + 5;
            if (isAtBottom) {
                tosCheckbox.disabled = false;
            }
        });
    }
});

    // 4. Превью загружаемой аватарки
    const avatarInput = document.getElementById("avatar-input");
    const avatarPreview = document.getElementById("avatar-preview");
    const registerForm = document.getElementById("register-form");

    if (avatarInput && avatarPreview) {
        avatarInput.addEventListener("change", () => {
            const file = avatarInput.files[0];
            if (file) {
                avatarPreview.src = URL.createObjectURL(file);
                avatarPreview.classList.remove("hidden");
            }
        });

        if (registerForm) {
            registerForm.addEventListener("reset", () => {
                avatarPreview.src = "";
                avatarPreview.classList.add("hidden");
                if (ageDisplay) ageDisplay.textContent = "0.00";
                if (userBox) userBox.style.backgroundColor = "#000";
                if (tosCheckbox) tosCheckbox.disabled = true;
            });
        }
    }
