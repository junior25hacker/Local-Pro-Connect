const getLocationBtn = document.getElementById("getLocationBtn");
const errorMsg = document.getElementById("locationError");
const manualAddress = document.getElementById("manualAddress");

getLocationBtn.addEventListener("click", () => {
  if (!navigator.geolocation) {
    showError("Your browser does not support location services.");
    return;
  }

  navigator.geolocation.getCurrentPosition(
    (position) => {
      document.getElementById("latitude").value = position.coords.latitude;
      document.getElementById("longitude").value = position.coords.longitude;
      errorMsg.style.display = "none";
      manualAddress.style.display = "none";
    },
    (error) => {
      showError("Location access denied. Please enter your address manually.");
      manualAddress.style.display = "block";
    }
  );
});

function showError(message) {
  errorMsg.textContent = message;
  errorMsg.style.display = "block";
}
