import { createApp } from 'vue';
import App from './App.vue';
import 'bootstrap/dist/css/bootstrap.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';
import 'jquery';
import router from './routers';
import axios from 'axios';
import '@/assets/css/style.css'; // This is the Global styles file

// Seting Base URL for API Requests
axios.defaults.baseURL = 'http://127.0.0.1:5000';

// Attaching JWT Token Before Every Request
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');

    if (token && !config.url.includes("/api/signup")) {
      config.headers = {
        ...config.headers,
        Authorization: `Bearer ${token}`,
      };
      console.log("🔹 Axios Sending Token:", token);
    } else if (config.url.includes("/api/signup")) {
      console.log(" Skipping JWT for Signup Request!");
    }

    return config;
  },
  (error) => {
    console.error(" Request Error:", error);
    return Promise.reject(error);
  }
);

//  Global Response Interceptor for Handling Errors
axios.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const status = error.response.status;
      const errorMsg = error.response.data.error || "";

      console.error(` API Error (${status}):`, error.response.data);

      // If user is BLOCKED (403) → Immediate logout
      if (status === 403 && errorMsg.includes("blocked")) {
        console.warn(" Your account has been blocked! Logging out...");
        alert("Your account has been blocked by the admin.");
        localStorage.clear();
        if (router.currentRoute.value.path !== "/login") {
          router.push("/login");
        }
        return Promise.reject(error);
      }

      // If user is UNAUTHORIZED (401) → Redirect to login
      if (status === 401) {
        console.warn(" Unauthorized! Redirecting to Login...");
        localStorage.clear();
        if (router.currentRoute.value.path !== "/login") {
          router.push("/login");
        }
      }
    } else {
      console.error(" Network Error:", error.message);
    }
    return Promise.reject(error);
  }
);

// Make sure its Correct Content-Type for All Requests
axios.defaults.headers.common['Content-Type'] = 'application/json';

// Applying the saved theme when the app loads
const savedTheme = localStorage.getItem('selectedTheme') || 'light';
document.documentElement.setAttribute('data-theme', savedTheme);

// Initializing Vue App
const app = createApp(App);
app.use(router);
app.mount('#app');
