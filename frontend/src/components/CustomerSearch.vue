<template>
  <div class="customer-request-search">
    <h1>My Service Requests</h1>

    <!-- Search Filters -->
    <div class="filters">
      <!-- Text Search -->
      <input type="text" v-model="searchQuery"
        placeholder="Search by service name, professional name, address, or pincode..." class="search-input" />

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
          <option value="accepted">Accepted</option>
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
          <th>Professional Name</th>
          <th>Professional Address</th>
          <th>Professional Zip Code</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="req in filteredRequests" :key="req.id">
          <td>{{ req.service_title }}</td>
          <td>{{ formatDate(req.request_date) }}</td>
          <td>{{ displayStatus(req.status) }}</td>
          <td>{{ req.professional_name }}</td>
          <td>{{ req.professional_address }}</td>
          <td>{{ req.professional_zip_code }}</td>
        </tr>
      </tbody>
    </table>
    <p v-if="filteredRequests.length === 0">No requests found.</p>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchQuery: "",
      searchDate: "",
      searchStatus: "all",
      requests: [],
    };
  },
  computed: {
    filteredRequests() {
      const statusMap = {
        pending: "requested",
        accepted: "accepted",
        "in progress": "in_progress",
        completed: "completed",
        rejected: "rejected",
      };

      const textQuery = this.searchQuery.toLowerCase().trim();
      return this.requests.filter(req => {
        // Text-based filtering
        const matchesText =
          !textQuery ||
          (req.service_title && req.service_title.toLowerCase().includes(textQuery)) ||
          (req.professional_name && req.professional_name.toLowerCase().includes(textQuery)) ||
          (req.professional_address && req.professional_address.toLowerCase().includes(textQuery)) ||
          (req.professional_zip_code && String(req.professional_zip_code).toLowerCase().includes(textQuery));

        // Date-based filtering
        let matchesDate = true;
        if (this.searchDate) {
          const requestDateStr = this.formatDateOnly(req.request_date);
          matchesDate = requestDateStr === this.searchDate;
        }

        // Status-based filtering (case-insensitive with map)
        let matchesStatus = true;
        if (this.searchStatus !== "all") {
          const mappedStatus = statusMap[this.searchStatus];
          // actual request status (lowercase)
          const reqStatus = req.status ? req.status.toLowerCase() : "";
          // Comparing with mappedStatus
          matchesStatus = reqStatus === mappedStatus;
        }
        return matchesText && matchesDate && matchesStatus;
      });
    }
  },
  mounted() {

    const customerId = localStorage.getItem("customerId");
    if (!customerId) {
      console.warn("Customer ID not found. Please log in properly.");
      return;
    }

    // fetching only requests for this customer
    axios.get(`/get_requests?customer_id=${customerId}`)
      .then(response => {
        this.requests = response.data;
      })
      .catch(error => {
        console.error("Error fetching customer requests:", error);
      });
  },
  methods: {
    formatDate(dateString) {
      if (!dateString) return "N/A";
      return new Date(dateString).toLocaleString();
    },
    formatDateOnly(dateString) {
      if (!dateString) return "";
      const d = new Date(dateString);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, '0');
      const day = String(d.getDate()).padStart(2, '0');
      return `${year}-${month}-${day}`;
    },
    // Showing "PENDING" instead of "REQUESTED"
    displayStatus(rawStatus) {
      if (!rawStatus) return "";
      const lower = rawStatus.toLowerCase();
      if (lower === "requested") return "PENDING";

      return rawStatus.toUpperCase();
    }
  }
};
</script>

<style src="@/assets/css/CustomerSearch.css"></style>
