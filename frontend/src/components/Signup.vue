<template>
  <div class="auth-container1">
    <!-- Left side with image slider -->
    <div class="image-slider1">
      <div class="overlay1"></div>
      <div class="slider-text title-text short-tagline">
        Elevate Everyday
      </div>
      <img :src="currentImage" class="slider-image1" />
    </div>

    <!-- Right side with register form -->
    <div class="form-container1">
      <h2 class="form-title">Welcome to ServiGo</h2>
      <h2>{{ dynamicTitle }}</h2>
      <form @submit.prevent="handleRegister">
        <input type="text" v-model="firstName" placeholder="First Name" required />
        <input type="text" v-model="lastName" placeholder="Last Name" required />
        <input type="text" v-model="username" placeholder="Username" required />
        <input type="email" v-model="email" placeholder="Email" required />
        <input type="password" v-model="password" placeholder="Password" required />
        <input type="text" v-model="phone" placeholder="Phone Number" required />
        <input type="text" v-model="address" placeholder="Address" required />
        <input type="text" v-model="zipCode" placeholder="Zip Code" required />

        <!-- Role Selection (with dynamic title) -->
        <div class="fields">
          <!-- Role + Years -->
          <select v-model="role" required @change="updateTitle" class="professional-fields">
            <option value="CUSTOMER">Customer</option>
            <option value="PROFESSIONAL">Professional</option>
          </select>

          <!-- Only showing this if role is PROFESSIONAL -->
          <input v-if="role === 'PROFESSIONAL'" type="number" v-model="experienceYears"
            placeholder="Years of Experience" required class="field2" />

          <!-- Full-width Service Type (only if PROFESSIONAL) -->
          <select v-if="role === 'PROFESSIONAL'" id="service" v-model="selectedService" required @focus="checkServices"
            class="field-full">
            <option disabled value="">
              <template v-if="services.length === 0">
                No services available currently.
              </template>
              <template v-else>-- Select a Service Type --</template>
            </option>
            <option v-for="service in services" :key="service.id" :value="service.id">
              {{ service.title }}
            </option>
          </select>

          <!--  Uploading File -->
          <input v-if="role === 'PROFESSIONAL'" type="file" @change="handlePortfolioUpload" accept=".pdf" required
            class="field3" />
        </div>

        <button type="submit">Sign Up</button>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-message">
          {{ successMessage }}
        </p>
      </form>
      <p>
        Already have an account?
        <router-link to="/login" @click="toggleLogin">Login</router-link>
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
      firstName: "",
      lastName: "",
      username: "",
      email: "",
      password: "",
      phone: "",
      address: "",
      zipCode: "",
      role: "CUSTOMER",

      selectedService: "",
      experienceYears: "",
      portfolioFile: "",

      // For feedback messages
      errorMessage: "",
      successMessage: "",
      dynamicTitle: "Register as Customer",

      // Image slider
      images: [
        require("@/assets/illustrations/Hairdresser.svg"),
        require("@/assets/illustrations/cleaning.svg"),
        require("@/assets/illustrations/Teacher.svg"),
      ],
      currentImageIndex: 0,

      // List of available services (fetched from backend)
      services: [],
    };
  },
  computed: {
    currentImage() {
      return this.images[this.currentImageIndex];
    },
  },
  mounted() {
    // Rotating images every 5 seconds
    setInterval(() => {
      this.currentImageIndex =
        (this.currentImageIndex + 1) % this.images.length;
    }, 5000);

    // Fetching available services from the backend for professional sign-up
    axios
      .get("http://127.0.0.1:5000/api/public/services")
      .then((response) => {
        this.services = response.data;
      })
      .catch((error) => {
        console.error("Error fetching services:", error);
      });
  },
  methods: {
    updateTitle() {
      // Updating dynamic title based on selected role
      this.dynamicTitle = `Register as ${this.role.charAt(0).toUpperCase() + this.role.slice(1).toLowerCase()
        }`;
    },
    handlePortfolioUpload(event) {
      const file = event.target.files[0];
      if (file && file.type === "application/pdf") {
        this.portfolioFile = file;
      } else {
        this.errorMessage = "Please select a valid PDF file.";
        this.portfolioFile = null;
      }
    },
    async handleRegister() {
      // Clearing previous messages
      this.errorMessage = "";
      this.successMessage = "";

      // Validating common fields
      if (
        !this.firstName ||
        !this.lastName ||
        !this.username ||
        !this.email ||
        !this.password ||
        !this.phone ||
        !this.address ||
        !this.zipCode
      ) {
        this.errorMessage = "All fields are required.";
        return;
      }

      // Signing up as PROFESSIONAL, ensuring a service is selected
      if (this.role === "PROFESSIONAL") {
        if (!this.selectedService) {
          this.errorMessage = "Please select a service type.";
          return;
        }
        // ensure services exist
        if (!this.services.length) {
          this.errorMessage =
            "No services available currently. Please try again later.";
          return;
        }
        if (!this.portfolioFile) {
          this.errorMessage = "Please upload a portfolio PDF.";
          return;
        }
      }

      const formData = new FormData();
      formData.append("first_name", this.firstName);
      formData.append("last_name", this.lastName);
      formData.append("username", this.username);
      formData.append("email", this.email);
      formData.append("password", this.password);
      formData.append("phone", this.phone);
      formData.append("address", this.address);
      formData.append("zip_code", this.zipCode);
      formData.append("role", this.role);

      if (this.role === "PROFESSIONAL") {
        formData.append("service_type", this.selectedService);
        formData.append("experience_years", this.experienceYears);
        formData.append("portfolio_file", this.portfolioFile);
      }

      try {
        // Sending the request with multipart/form-data
        const response = await axios.post(
          "http://127.0.0.1:5000/api/signup",
          formData,
          {
            headers: {
              "Content-Type": "multipart/form-data",
            },
          }
        );
        console.log(" Registration successful:", response.data);
        this.successMessage =
          "Registration successful! Pending admin approval.";

        // Wait for UI updates before redirecting
        await this.$nextTick();
        setTimeout(() => {
          this.$router.push("/login");
        }, 2500);
      } catch (error) {
        console.error(" Registration failed:", error);
        if (error.response) {
          this.errorMessage =
            error.response.data.message || "Signup failed. Try again.";
        } else {
          this.errorMessage = "Server error. Please try again later.";
        }
      }
    },
    toggleLogin() {
      this.$router.push("/login");
    },
    checkServices() {
      if (this.services.length === 0) {
        alert("No services available currently. Please check back later.");
      }
    },
  },
};
</script>

<style src="@/assets/css/signup.css"></style>
