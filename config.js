// Check if we are running locally or on a server
const API_BASE_URL = window.location.hostname === "127.0.0.1" || window.location.hostname === "localhost"
    ? "http://127.0.0.1:5000" 
    : "https://your-production-api.com";