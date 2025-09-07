<template>
  <div class="professional-request-search">
    <h1>My Received Requests</h1>

    <!-- Search Filters -->
    <div class="filters">
      <!-- Text Search: searches service title, customer name, customer address, customer zip code -->
      <input type="text" v-model="searchQuery"
        placeholder="Search by service name, customer name, address, or zip code..." class="search-input" />

      <!-- Date Filter -->
      <label class="date-label">
        Filter by Date:
        <input type="date" v-model="searchDate" class="date-input" />
      </label>

      <!-- Status Filter -->
      <label class="status-label">
        Filter by Status:
        <select v-model="searchStatus" class="status-dropdown">
          <option value="all">All</option>
          <option value="pending">Pending</option>
          <option value="in progress">In Progress</option>
          <option value="completed">Completed</option>
          <option value="rejected">Rejected</option>
        </select>
      </label>
    </div>

    <!-- Results Table -->
    <table class="requests-table">
      <thead>
        <tr>
          <th>Service Title</th>
          <th>Request Date</th>
          <th>Status</th>
          <th>Customer Name</th>
          <th>Customer Address</th>
          <th>Customer Zip Code</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="req in filteredRequests" :key="req.id">
          <td>{{ req.service_title }}</td>
          <td>{{ formatDate(req.request_date) }}</td>
          <td>{{ req.status }}</td>
          <td>{{ req.customer_name }}</td>
          <td>{{ req.customer_address }}</td>
          <td>{{ req.customer_zip_code }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="filteredRequests.length === 0">No requests found.</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: "ProfessionalRequests",
  data() {
    return {
      // Filters
      searchQuery: "",
      searchDate: "",
      searchStatus: "all",

      // Requests array fetched from the backend
      requests: [],
      professionalId: null
    };
  },
  computed: {
    filteredRequests() {
      const textQuery = this.searchQuery.toLowerCase().trim();
      return this.requests.filter(req => {
        // Text-based filtering: service_title, customer_name, customer_address, customer_zip_code
        const matchesText =
          !textQuery ||
          (req.service_title && req.service_title.toLowerCase().includes(textQuery)) ||
          (req.customer_name && req.customer_name.toLowerCase().includes(textQuery)) ||
          (req.customer_address && req.customer_address.toLowerCase().includes(textQuery)) ||
          (req.customer_zip_code && String(req.customer_zip_code).toLowerCase().includes(textQuery));

        // Date-based filtering: compare YYYY-MM-DD portion of request_date to searchDate
        let matchesDate = true;
        if (this.searchDate) {
          const requestDateStr = this.formatDateOnly(req.request_date);
          matchesDate = requestDateStr === this.searchDate;
        }

        // Status-based filtering (case-insensitive)
        let matchesStatus = true;
        if (this.searchStatus !== "all") {
          const reqStatus = req.status ? req.status.toLowerCase() : "";
          const filterStatus = this.searchStatus.toLowerCase();
          matchesStatus = reqStatus === filterStatus;
        }

        return matchesText && matchesDate && matchesStatus;
      });
    }
  },
  mounted() {
    const storedId = localStorage.getItem("professionalId");
    if (!storedId) {
      console.warn("No professional ID found in localStorage. Please set it or retrieve it from route/JWT.");
      return;
    }
    this.professionalId = storedId;

    axios
      .get(`/get_requests?professional_id=${this.professionalId}`)
      .then(response => {
        console.log("Fetched requests:", response.data);
        this.requests = response.data;
      })
      .catch(error => {
        console.error("Error fetching professional requests:", error);
      });
  },
  methods: {
    // Formating full date/time for display.
    formatDate(dateString) {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleString();
    },
    // Extracting YYYY-MM-DD portion for date comparisons.
    formatDateOnly(dateString) {
      if (!dateString) return "";
      const d = new Date(dateString);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    }
  }
};

</script>

<style src="@/assets/css/ProfessionalSearch.css"></style>
