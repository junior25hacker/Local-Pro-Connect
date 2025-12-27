document.addEventListener("DOMContentLoaded", () => {
    const statusText = document.getElementById("trackingStatus");

    if (!navigator.geolocation) {
        statusText.textContent = "Geolocation is not supported by your browser.";
        return;
    }

    statusText.textContent = "Detecting your location...";

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;

            statusText.textContent = `Your location detected: (${latitude}, ${longitude})`;

            // Optional: store for later backend/map use
            console.log("User Location:", latitude, longitude);
        },
        (error) => {
            statusText.textContent = "Location access denied. Please enable location permissions.";
        }
    );
});
