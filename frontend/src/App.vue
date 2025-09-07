<template>
  <div id="app">
    <Navbar v-if="!isAuthPage" />
    <router-view />
    <!-- Render Navbar only if the current route does not seting  hideNavbar -->
  </div>
</template>

<script>
import { useRoute } from "vue-router";
import { computed } from "vue";
import Navbar from "./components/Navbar.vue";



export default {
  name: "App",
  components: {
    Navbar,
  },
  setup() {
    const route = useRoute();
    const isAuthPage = computed(() => ["/login", "/signup", "/profile", "/create-service"].includes(route.path));

    return { isAuthPage };
  }
};
</script>

<style src="@/assets/css/style.css"></style>
