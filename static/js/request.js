
document.addEventListener("DOMContentLoaded", function () {
    
    // ===========================
    // PRICE SLIDER
    // ===========================
    const priceRanges = [
        { label: "500 – 5,000", min: 500, max: 5000 },
        { label: "5,000 – 10,000", min: 5000, max: 10000 },
        { label: "10,000 – 20,000", min: 10000, max: 20000 },
        { label: "20,000 – 40,000", min: 20000, max: 40000 },
        { label: "40,000 – 60,000", min: 40000, max: 60000 },
        { label: "60,000 – 80,000", min: 60000, max: 80000 },
        { label: "80,000 – 100,000", min: 80000, max: 100000 },
        { label: "100,000+", min: 100000, max: null },
    ];

    document.addEventListener("DOMContentLoaded", function () {
    const priceSelect = document.getElementById("id_price_range");
    if (priceSelect && window.priceRanges) {
        const sliderContainer = document.createElement("div");
        sliderContainer.classList.add("price-slider-container");

        const slider = document.createElement("input");
        slider.type = "range";
        slider.min = 0;
        slider.max = priceRanges.length - 1;
        slider.value = 0;
        slider.step = 1;
        slider.classList.add("price-slider");

        const display = document.createElement("span");
        display.classList.add("price-display");
        display.textContent = priceRanges[0].label;

        sliderContainer.appendChild(slider);
        sliderContainer.appendChild(display);
        priceSelect.parentNode.insertBefore(sliderContainer, priceSelect.nextSibling);

        // Hide original select
        priceSelect.style.display = "none";

        // Populate select dynamically from priceRanges
        priceSelect.innerHTML = "";
        priceRanges.forEach(pr => {
            const option = document.createElement("option");
            option.value = pr.id;
            option.text = pr.label;
            priceSelect.appendChild(option);
        });

        slider.addEventListener("input", function () {
            const index = parseInt(slider.value);
            display.textContent = priceRanges[index].label;
            priceSelect.value = priceRanges[index].id;
        });
    }

    // Existing urgent toggle and photo preview logic...
});

    // ===========================
    // URGENT TOGGLE
    // ===========================
    const urgentCheckbox = document.getElementById("id_urgent");
    const urgentLabel = document.querySelector("label[for='id_urgent']");

    if (urgentCheckbox && urgentLabel) {
        urgentLabel.addEventListener("click", function () {
            urgentCheckbox.checked = !urgentCheckbox.checked;
            // CSS handles pill active state automatically
        });
    }

    // ===========================
    // PHOTO PREVIEW (OPTIONAL)
    // ===========================
    const photoInput = document.getElementById("id_photos");
    if (photoInput) {
        const previewContainer = document.createElement("div");
        previewContainer.classList.add("photo-preview-container");
        photoInput.parentNode.insertBefore(previewContainer, photoInput.nextSibling);

        photoInput.addEventListener("change", function () {
            previewContainer.innerHTML = ""; // Clear previous previews
            const files = Array.from(photoInput.files);

            files.forEach(file => {
                if (!file.type.startsWith("image/")) return;

                const reader = new FileReader();
                reader.onload = function (e) {
                    const img = document.createElement("img");
                    img.src = e.target.result;
                    img.style.height = "80px";
                    img.style.width = "80px";
                    img.style.objectFit = "cover";
                    img.style.marginRight = "8px";
                    img.style.borderRadius = "8px";
                    previewContainer.appendChild(img);
                };
                reader.readAsDataURL(file);
            });
        });
    }
});