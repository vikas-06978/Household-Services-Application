<template>
  <div class="profile-page">
    <div class="profile-container">
      <!-- Profile Image -->
      <div class="profile-image-container">
        <img :src="profileImage" alt="Profile Image" class="profile-image" />
      </div>

      <!-- Profile Details -->
      <div class="profile-details">
        <h1 class="username">👋 Hello, {{ username }}!</h1>
        <h3 class="role">⚡ {{ formattedRole }}</h3>

        <!-- Admin Profile -->
        <div v-if="userRole === 'ADMIN'" class="profile-info">
          <p> <strong>Username:</strong> {{ username }}</p>
          <p> <strong>Registered On:</strong> {{ registeredOn }}</p>
        </div>

        <!-- Customer Profile -->
        <div v-else-if="userRole === 'CUSTOMER'" class="profile-info">
          <p> <strong>Full Name:</strong> {{ fullName }}</p>
          <p><strong>Address:</strong> {{ address }}</p>
          <p><strong>Zip Code:</strong> {{ zipCode }}</p>
          <p><strong>Registered On:</strong> {{ registeredOn }}</p>
        </div>

        <!-- Professional Profile -->
        <div v-else-if="userRole === 'PROFESSIONAL'" class="profile-info">
          <p><strong>Full Name:</strong> {{ fullName }}</p>
          <p><strong>Service Type:</strong> {{ service_type }}</p>
          <p><strong>Experience:</strong> {{ experienceYears }} years</p>
          <p class="portfolio-link">
            <strong>Portfolio:</strong>
            <button class="portfolio-btn" @click="downloadPortfolio(portfolioLink)">
              View Portfolio
            </button>
          </p>

          <p><strong>Average Rating:</strong> {{ averageRating }}/5</p>
          <p><strong>Registered On:</strong> {{ registeredOn }}</p>
        </div>

        <!-- Buttons Section -->
        <div class="button-group">
          <button @click="logout" class="logout-btn">⏻ Logout</button>
          <button @click="goBack" class="back-btn">⬅ Dashboard</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from "axios";

export default {
  data() {
    return {
      username: localStorage.getItem("username") || "Guest",
      userRole: localStorage.getItem("role") || null,
      registeredOn: "Fetching...",
      fullName: localStorage.getItem("fullName") || "N/A",
      address: localStorage.getItem("address") || "N/A",
      zipCode: localStorage.getItem("zipCode") || "N/A",
      service_type: localStorage.getItem("service_type") || "N/A",
      experienceYears: localStorage.getItem("experienceYears") || "0",
      portfolioLink: localStorage.getItem("portfolioLink") || "#",
      averageRating: localStorage.getItem("averageRating") || "N/A",
      token: null,
    };
  },
  computed: {
    formattedRole() {
      return this.userRole
        ? this.userRole.charAt(0).toUpperCase() + this.userRole.slice(1)
        : "Unknown";
    },
    profileImage() {
      const role = (this.userRole || "").toLowerCase();
      const images = {
        admin: require("@/assets/Images/admin-avatar.png"),
        customer: require("@/assets/Images/customer-avatar.png"),
        professional: require("@/assets/Images/professional-avatar.png"),
      };
      return images[role] || require("@/assets/Images/default-avatar.png");
    },
  },
  mounted() {
    this.getTokenAndFetchUser();
  },
  methods: {
    downloadPortfolio(filename) {
      const token = localStorage.getItem("token");

      fetch(`http://127.0.0.1:5000/uploads/${filename}`, {
        method: "GET",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error("Failed to download portfolio.");
          }
          return response.blob();
        })
        .then((blob) => {
          const url = window.URL.createObjectURL(blob);
          window.open(url, "_blank");
        })
        .catch((err) => {
          console.error("Error:", err);
          alert("Unable to view portfolio PDF.");
        });
    },

    getTokenAndFetchUser() {
      // Fetching the token dynamically at the time of request
      this.token = localStorage.getItem("token");

      if (!this.token) {
        console.error(
          "No JWT token found at mount. Redirecting to login..."
        );
        this.$router.push("/login");
        return;
      }

      console.log(" Token Found. Fetching User Details...");
      this.fetchUserDetails();
    },
    async fetchUserDetails() {
      try {
        console.log(" Fetching user details for:", this.username);

        if (!this.token) {
          console.error(" Token missing before API call! Redirecting...");
          this.$router.push("/login");
          return;
        }

        const response = await axios.get(
          `http://127.0.0.1:5000/api/user/${this.username}`,
          { headers: { Authorization: `Bearer ${this.token}` } }
        );

        console.log(" API Response:", response.data);

        // If user is blocked, logging them out immediately
        if (response.data.is_blocked) {
          console.warn(" Your account has been blocked! Logging out...");
          alert("Your account has been blocked by the admin.");
          localStorage.clear();
          this.$router.push("/login");
          return;
        }

        // Storing the fetched profile details
        this.fullName = response.data.full_name || "N/A";
        this.service_type = response.data.service_type || "N/A";
        this.experienceYears = response.data.experience_years || "0";
        this.portfolioLink = response.data.portfolio_link || "";
        console.log("Fetched portfolio_link:", response.data.portfolio_link);

        this.averageRating = response.data.average_rating ?? "N/A";
        this.registeredOn = response.data.registered_on || "N/A";
        this.address = response.data.address || "N/A";
        this.zipCode = response.data.zip_code || "N/A";

        // Updating localStorage for persistence
        localStorage.setItem("fullName", this.fullName);
        localStorage.setItem("service_type", this.service_type);
        localStorage.setItem("experienceYears", this.experienceYears);
        localStorage.setItem("portfolioLink", this.portfolioLink);
        localStorage.setItem("averageRating", this.averageRating);
        localStorage.setItem("address", this.address);
        localStorage.setItem("zipCode", this.zipCode);
      } catch (error) {
        console.error(" Failed to fetch user details:", error);
        if (error.response && error.response.status === 401) {
          console.warn(" Unauthorized! Redirecting to login...");
          localStorage.clear();
          this.$router.push("/login");
        }
        this.fullName = "N/A";
        this.service_type = "N/A";
        this.experienceYears = "0";
        this.portfolioLink = "#";
        this.averageRating = "N/A";
      }
    },

    logout() {
      localStorage.clear();
      this.$router.push("/login");
    },
    goBack() {
      const dashboardRoutes = {
        admin: "/admin/dashboard",
        customer: "/customer/dashboard",
        professional: "/professional/dashboard",
      };
      this.$router.push(
        dashboardRoutes[this.userRole.toLowerCase()] || "/login"
      );
    },
  },
  watch: {
    // Watching for token changes dynamically
    token(newToken) {
      if (!newToken) {
        console.warn(" Token missing! Redirecting to login...");
        this.$router.push("/login");
      }
    },
  },
};
</script>

<style src="@/assets/css/profile.css"></style>
