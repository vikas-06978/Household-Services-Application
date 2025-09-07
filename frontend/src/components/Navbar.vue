<template>
  <!-- Navbar Container -->
  <div class="navbar-container">
    <!-- Platform Name  -->
    <router-link class="navbar-brand platform-name" :to="homeLink" exact-active-class="">⚡ServiGo</router-link>

    <!-- Navbar  -->
    <nav class="navbar navbar-expand-lg navbar-light rounded-pill custom-navbar">
      <div class="container-fluid">
        <!-- Centered Navigation Links -->
        <div class="mx-auto navbar-center">
          <ul class="navbar-nav">
            <li class="nav-item">
              <router-link class="nav-link" :to="homeLink">Home</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="searchLink">Search</router-link>
            </li>
            <li class="nav-item">
              <router-link class="nav-link" :to="summaryLink">Summary</router-link>
            </li>
          </ul>
        </div>
      </div>
    </nav>

    <!-- Profile & Logout Outside Navbar  -->
    <div class="user-controls navbar-right">
      <button @click="toggleTheme" class="theme-toggle-btn">
        {{ currentTheme === "light" ? "🌙 Dark" : "☀️ Light" }}
      </button>
      <span v-if="isLoggedIn" class="profile-text1">Welcome, {{ username }}
        <span v-if="subscriptionStatus === 'active'" class="badge bg-warning text-dark">
          👑 Premium
        </span>
      </span>
      <router-link v-if="isLoggedIn" to="/profile" class="profile-text" @click="goToProfile">
        👤PROFILE <span class="arrow">↗</span></router-link>
      <router-link v-else class="nav-link login-btn" to="/login">Login</router-link>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      currentTheme: localStorage.getItem("selectedTheme") || "light",
      userRole: localStorage.getItem("role") || null,
      username: localStorage.getItem("username") || "Guest",
      subscriptionStatus:
        localStorage.getItem("subscriptionStatus") || "inactive",
    };
  },
  computed: {
    isLoggedIn() {
      return this.userRole !== null;
    },
    homeLink() {
      return this.getRouteBasedOnRole("home");
    },

    searchLink() {
      return this.getRouteBasedOnRole("search");
    },
    summaryLink() {
      return this.getRouteBasedOnRole("summary");
    },
    showNavbar() {
      return !this.$route.meta.hideNavbar;
    },
  },
  mounted() {

    document.documentElement.setAttribute("data-theme", this.currentTheme);

    this.subscriptionStatus =
      localStorage.getItem("subscriptionStatus") || "inactive";
  },
  methods: {
    toggleTheme() {
      this.currentTheme = this.currentTheme === "light" ? "dark" : "light";
      document.documentElement.setAttribute("data-theme", this.currentTheme);
      localStorage.setItem("selectedTheme", this.currentTheme);
    },

    getRouteBasedOnRole(type) {
      const role = (this.userRole || "").toLowerCase();
      const routes = {
        home: {
          admin: "/admin/dashboard",
          customer: "/customer/dashboard",
          professional: "/professional/dashboard",
        },
        search: {
          admin: "/admin/search",
          customer: "/customer/search",
          professional: "/professional/search",
        },
        summary: {
          admin: "/admin/summary",
          customer: "/customer/summary",
          professional: "/professional/summary",
        },
      };
      return routes[type][role] || "/login";
    },
    goToProfile() {
      this.$router.push("/profile");
    },
    logout() {
      localStorage.removeItem("role");
      localStorage.removeItem("username");
      localStorage.removeItem("token");
      localStorage.removeItem("subscriptionStatus");
      this.userRole = null;
      this.username = "Guest";
      this.subscriptionStatus = "inactive";
      this.$router.push("/login");
    },
  },
};
</script>

<style src="@/assets/css/navbar.css"></style>
