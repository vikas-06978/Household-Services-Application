<template>
  <div class="create-service">
    <button class="back-btn" @click="$router.back()">Back</button>
    <h2>Create a New Service</h2>
    <form @submit.prevent="submitService">
      <div>
        <label for="title">Service Name:</label>
        <select v-model="selectedService" @change="autoFillCategory" required>
          <option value="" disabled>Select a Service</option>
          <option v-for="svc in predefinedServices" :key="svc.title" :value="svc.title">
            {{ svc.title }}
          </option>
        </select>
      </div>
      <div>
        <label for="description">Description:</label>
        <textarea id="description" v-model="service.description"></textarea>
      </div>
      <div>
        <label for="category">Category:</label>
        <input type="text" v-model="selectedCategory" required />
      </div>
      <div>
        <label for="price">Price:</label>
        <input type="number" step="0.01" id="price" v-model="service.price" />
      </div>
      <button type="submit">Create Service</button>
    </form>
    <p v-if="successMessage" class="success">{{ successMessage }}</p>
    <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
  </div>
</template>

<script>
import axios from "axios";
import { nextTick } from "vue";

export default {
  data() {
    return {
      service: {
        title: "",
        description: "",
        category: "",
        price: 0,
      },
      successMessage: "",
      errorMessage: "",

      selectedService: "",
      selectedCategory: "",
      predefinedServices: [
        { title: "Cleaning", category: "Home Services" },
        { title: "Haircut", category: "Personal Care" },
        { title: "Electrician", category: "Home Services" },
        { title: "Plumber", category: "Home Services" },
        { title: "AC Repair", category: "Appliance Repair" },
        { title: "Tuition", category: "Education" },
        { title: "Pest Control", category: "Home Services" },
        { title: "Makeup Artist", category: "Personal Care" },
        { title: "Carpenter", category: "Home Services" },
        { title: "Home Tutor", category: "Education" },
      ],
    };
  },
  methods: {
    autoFillCategory() {
      const selected = this.predefinedServices.find(
        (svc) => svc.title === this.selectedService
      );
      this.selectedCategory = selected ? selected.category : "";
    },
    createService() {
      if (!this.selectedService) {
        alert("Please select a Service Name.");
        return;
      }
      // Form submission logic 
      const payload = {
        title: this.selectedService,
        category: this.selectedCategory,
        description: this.description,
        price: this.price,
      };
    },
    async submitService() {
      // Clearing messages
      this.errorMessage = "";
      this.successMessage = "";

      this.service.title = this.selectedService;
      this.service.category = this.selectedCategory;
      // Validating that title is provided
      if (!this.service.title) {
        this.errorMessage = "Service title is required.";
        return;
      }

      try {
        const response = await axios.post(
          "http://127.0.0.1:5000/api/admin/services",
          this.service,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        );
        console.log(" Service created successfully:", response.data);
        this.successMessage = response.data.message;

        // Reseting the form fields
        this.service.title = "";
        this.service.description = "";
        this.service.category = "";
        this.service.price = 0;
        this.selectedService = "";
        this.selectedCategory = "";

        await nextTick();
      } catch (error) {
        console.error(" Error creating service:", error);
        this.errorMessage =
          error.response?.data.error ||
          "Error creating service. Please try again.";
      }
    },
  },
};
</script>

<style src="@/assets/css/CreateService.css"></style>
