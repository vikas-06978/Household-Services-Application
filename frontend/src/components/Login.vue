<template>
  <div class="auth-container">
    <!-- Left side with image slider -->
    <div class="image-slider">
      <div class="overlay"></div>
      <div class="slider-text title-text short-tagline">
        Elevate Everyday
      </div>
      <img :src="currentImage" class="slider-image" />
    </div>

    <!-- Right side with form -->
    <div class="form-container">
      <h2 class="form-title">Welcome to ServiGo</h2>
      <h2>{{ dynamicTitle }}</h2>
      <form @submit.prevent="handleLogin">
        <input type="text" v-model="username" placeholder="Username" required />
        <input type="password" v-model="password" placeholder="Password" required />
        <select v-model="role" required @click="updateTitle">
          <option disabled value="">▼ Select Role</option>
          <option value="ADMIN">Admin</option>
          <option value="CUSTOMER">Customer</option>
          <option value="PROFESSIONAL">Professional</option>
        </select>
        <button type="submit">Login</button>
        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
      </form>
      <p>
        Don't have an account?
        <router-link to="/signup" @click="toggleSignup">Sign Up</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import { nextTick } from "vue";

export default {
  data() {
    return {
      username: "",
      password: "",
      role: "",
      errorMessage: "",
      dynamicTitle: "Login as Admin",
      images: [
        require("@/assets/illustrations/Hairdresser.svg"),
        require("@/assets/illustrations/cleaning.svg"),
        require("@/assets/illustrations/Teacher.svg"),
      ],
      currentImageIndex: 0,
    };
  },
  computed: {
    currentImage() {
      return this.images[this.currentImageIndex];
    },
  },
  mounted() {
    setInterval(() => {
      this.currentImageIndex =
        (this.currentImageIndex + 1) % this.images.length;
    }, 5000);
  },
  methods: {
    updateTitle() {
      this.dynamicTitle = `Login as ${this.role.charAt(0).toUpperCase() + this.role.slice(1)
        }`;
    },
    async handleLogin() {
      if (!this.username || !this.password) {
        this.errorMessage = "Please enter your username and password.";
        return;
      }

      try {
        const response = await axios.post("http://127.0.0.1:5000/api/login", {
          username: this.username,
          password: this.password,
          role: this.role,
        });

        const data = response.data;
        console.log(" API Response:", data);

        if (data.is_blocked) {
          this.errorMessage = "Your account has been blocked. Contact support.";
          return;
        }

        if (!data.is_active && this.role !== "ADMIN") {
          this.errorMessage = "Your account is pending admin approval.";
          return;
        }

        localStorage.setItem("token", data.token);
        localStorage.setItem("role", data.role);
        localStorage.setItem("username", data.username);
        localStorage.setItem("registered_on", data.registered_on);

        // Storing Professional ID if role is PROFESSIONAL
        if (data.role === "PROFESSIONAL" && data.professional_id) {
          console.log("Storing Professional ID:", data.professional_id);
          localStorage.setItem("professionalId", data.professional_id);
        }
        // Storing Customer ID if role is CUSTOMER
        else if (data.role === "CUSTOMER" && data.customer_id) {
          console.log(" Storing Customer ID:", data.customer_id);
          localStorage.setItem("customerId", data.customer_id);
        } else {
          console.error(" Required ID is missing in API response.");
        }

        const roleRedirects = {
          ADMIN: "/admin/dashboard",
          CUSTOMER: "/customer/dashboard",
          PROFESSIONAL: "/professional/dashboard",
        };

        this.$router.push(roleRedirects[data.role] || "/login");
      } catch (error) {
        console.error(" Login error:", error);
        if (error.response) {
          this.errorMessage =
            error.response.data.error || "Login failed. Try again.";
        } else {
          this.errorMessage = "Server error. Please try again later.";
        }
      }
    },
    toggleSignup() {
      this.$router.push("/signup");
    },
  },
};
</script>

<style src="@/assets/css/login.css"></style>
