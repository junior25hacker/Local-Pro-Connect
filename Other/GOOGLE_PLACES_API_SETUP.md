# Google Places API Key Setup

To enable city/address autocomplete using Google Places in your Django backend:

1. **Get a Google API Key**
   - Go to https://console.cloud.google.com/
   - Create a project (if you don't have one)
   - Enable the "Places API" for your project
   - Go to "APIs & Services > Credentials" and create an API key
   - Restrict the key to HTTP referrers or IPs for security

2. **Set the API Key in Django**
   - Open `config/settings.py`
   - Set your key as an environment variable (recommended):
     
     On Windows Command Prompt:
     ```cmd
     set GOOGLE_PLACES_API_KEY=your_actual_key_here
     ```
     Or in PowerShell:
     ```powershell
     $env:GOOGLE_PLACES_API_KEY="your_actual_key_here"
     ```
   - Or, for development only, you can directly edit `settings.py`:
     ```python
     GOOGLE_PLACES_API_KEY = os.environ.get('GOOGLE_PLACES_API_KEY', 'YOUR_GOOGLE_PLACES_API_KEY_HERE')
     ```
     Replace `'YOUR_GOOGLE_PLACES_API_KEY_HERE'` with your real key.

3. **Restart your Django server** after setting the environment variable or editing settings.

4. **Security Note:**
   - Never commit your real API key to public repositories.
   - Always use environment variables for production.

---

If you have any issues, check the Django server logs for errors related to the Places API.
