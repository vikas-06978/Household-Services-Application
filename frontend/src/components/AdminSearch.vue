<template>
  <div class="admin-search">
    <h1 class="search-title">Admin Search</h1>

    <!-- Search Bar & Filters -->
    <div class="search-container">
      <input type="text" v-model="searchQuery" placeholder="Search across fields..." class="search-input" />

      <select v-model="searchCategory" class="search-dropdown">
        <option value="users">All Users</option>
        <option value="professionals">Professionals</option>
        <option value="customers">Customers</option>
        <option value="services">Services</option>
        <option value="requests">Service Requests</option>
      </select>

      <select v-model="searchFilter" class="filter-dropdown">
        <option value="all">All</option>
        <option value="pending">Pending</option>
        <option value="approved">Approved</option>
        <option value="blocked">Blocked</option>
      </select>

      <select v-model="sortBy" class="sort-dropdown">
        <option value="name">Sort by Name</option>
        <option value="date">Sort by Date</option>
        <option value="status">Sort by Status</option>
      </select>

      <button class="search-btn" @click="performSearch">Search</button>
    </div>

    <!-- Results Table -->
    <div class="search-results">
      <h2>📋 Search Results</h2>
      <table v-if="filteredResults.length > 0">
        <thead>
          <tr>
            <th v-for="col in tableColumns" :key="col.field">{{ col.label }}</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="result in filteredResults" :key="result.id">
            <td v-for="col in tableColumns" :key="col.field">
              {{ formatField(col.field, result[col.field]) }}
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No results found.</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  data() {
    return {
      searchQuery: "",
      searchCategory: "users",
      searchFilter: "all",
      sortBy: "name",
      results: [] // Fetching data from the backend
    };
  },
  computed: {
    // Defining the table headers (columns) based on the current category
    tableColumns() {
      switch (this.searchCategory) {
        case "users":
          return [
            { label: "Name", field: "name" },
            { label: "Category", field: "role" },
            { label: "Active", field: "is_active" },
            { label: "Blocked", field: "is_blocked" }
          ];
        case "professionals":
          return [
            { label: "Name", field: "full_name" },
            { label: "Zip Code", field: "zip_code" },
            { label: "Address", field: "address" },
            { label: "Experience", field: "experience_years" },
            { label: "Rating", field: "average_rating" }
          ];
        case "customers":
          return [
            { label: "Full Name", field: "full_name" },
            { label: "Address", field: "address" },
            { label: "Zip Code", field: "zip_code" }
          ];
        case "services":
          return [
            { label: "Title", field: "title" },
            { label: "Price", field: "price" },
            { label: "Category", field: "category" },
            { label: "Created At", field: "created_at" }
          ];
        case "requests":
          return [
            { label: "Service", field: "service_title" },
            { label: "Status", field: "status" },
            { label: "Remarks", field: "remarks" },
            { lebel: "Rating", field: "rating" },
            { label: "Request Date", field: "request_date" },
            { label: "Completion Date", field: "completion_date" }
          ];
        default:
          return [];
      }
    },
    // Filtering and sorting the results based on searchQuery, searchFilter, and sortBy
    filteredResults() {
      // filtering by search query and by searchFilter 
      let filtered = this.results.filter(item => {
        // checking across all displayed fields
        let searchStr = this.searchQuery.toLowerCase();
        if (!searchStr) return true;
        return this.tableColumns.some(col => {
          let fieldValue = item[col.field];
          return fieldValue !== null && fieldValue !== undefined &&
            String(fieldValue).toLowerCase().includes(searchStr);
        });
      });

      if (this.searchFilter !== "all") {
        filtered = filtered.filter(item => {
          // For users, checking the "is_blocked" status when filtering by "blocked"
          // Or "is_active" for "approved" 
          if (this.searchCategory === "users") {
            if (this.searchFilter === "blocked") {
              return item.is_blocked;
            } else if (this.searchFilter === "approved") {
              return item.is_active;
            }
          }
          // For other categories, checking a "status" field if it exists
          return item.status && item.status.toLowerCase() === this.searchFilter;
        });
      }

      // Sorting logic based on sortBy
      if (this.sortBy === "name") {
        filtered.sort((a, b) => {
          let aVal = "";
          let bVal = "";
          if (this.searchCategory === "users") {
            aVal = a.name || "";
            bVal = b.name || "";
          } else if (this.searchCategory === "professionals" || this.searchCategory === "customers") {
            aVal = a.full_name || "";
            bVal = b.full_name || "";
          } else if (this.searchCategory === "services") {
            aVal = a.title || "";
            bVal = b.title || "";
          } else if (this.searchCategory === "requests") {
            aVal = a.service_title || "";
            bVal = b.service_title || "";
          }
          return aVal.toLowerCase().localeCompare(bVal.toLowerCase());
        });
      } else if (this.sortBy === "date") {
        filtered.sort((a, b) => {
          let aDate = new Date(a.created_at || a.request_date || 0);
          let bDate = new Date(b.created_at || b.request_date || 0);
          return bDate - aDate;
        });
      } else if (this.sortBy === "status") {
        filtered.sort((a, b) => {
          let aStatus = String(a.status || "").toLowerCase();
          let bStatus = String(b.status || "").toLowerCase();
          return aStatus.localeCompare(bStatus);
        });
      }

      return filtered;
    }
  },
  watch: {
    searchCategory(newCategory) {
      this.fetchResults(newCategory);
    }
  },
  mounted() {
    this.fetchResults(this.searchCategory);
  },
  methods: {
    // Fetching data from the appropriate endpoints based on the category.
    fetchResults(category) {
      let endpoint = "";
      if (category === "users") {
        endpoint = "/api/admin/manage_users";
      } else if (category === "professionals") {
        endpoint = "/api/admin/professionals";
      } else if (category === "customers") {
        endpoint = "/api/admin/customers";
      } else if (category === "services") {
        endpoint = "/api/admin/services";
      } else if (category === "requests") {
        endpoint = "/api/admin/service_requests";
      }
      axios.get(endpoint)
        .then(response => {
          this.results = response.data;
        })
        .catch(error => {
          console.error("Error fetching data:", error);
        });
    },
    performSearch() {
      this.fetchResults(this.searchCategory);
    },
    // Formating field values for displaying (booleans and dates)
    formatField(field, value) {
      if (field === "is_active" || field === "is_blocked") {
        return value ? "Yes" : "No";
      }
      if (["created_at", "request_date", "completion_date"].includes(field)) {
        if (value) return new Date(value).toLocaleString();
      }
      return value;
    }
  }
};
</script>

<style src="@/assets/css/AdminSearch.css"></style>
