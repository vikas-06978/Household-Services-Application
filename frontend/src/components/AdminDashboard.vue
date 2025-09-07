<template>
  <div class="admin-dashboard ">
    <header class="header-bar">
      <h1 class="dashboard-title admin-banner text-center mb-4 ">Admin Dashboard</h1>
      <p class="text-muted platform-subtitle">Here’s what’s happening across your platform today.</p>
      <button class="report-btn" @click="downloadReport">
        Download Reports
      </button>
    </header>

    <!-- Dashboard Overview -->
    <section class="dashboard-section">
      <h2>Overview</h2>
      <div class="summary-cards">
        <div class="summary-card">
          <h3>Users</h3>
          <p>{{ totalUsers }}</p>
        </div>
        <div class="summary-card">
          <h3>Professionals</h3>
          <p>{{ totalProfessionals }}</p>
        </div>
        <div class="summary-card">
          <h3>Requests</h3>
          <p>{{ pendingRequests }} Pending</p>
        </div>
        <div class="summary-card">
          <h3>Revenue</h3>
          <p>${{ totalRevenue }}</p>
        </div>
      </div>
    </section>

    <!-- Pending User Approvals -->
    <section class="dashboard-section">
      <h2><i class="fas fa-user-clock"></i> Pending Approvals</h2>
      <table class="styled-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Address</th>
            <th>Phone</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="user in pendingUsers" :key="user.id">
            <td>{{ user.first_name }} {{ user.last_name }}</td>
            <td>{{ user.email_id }}</td>
            <td>{{ user.address }}</td>
            <td>{{ user.phone }}</td>
            <td>
              <button class="btn btn-success btn-approve action-button approve" @click="approveUser(user.id)">
                Approve
              </button>
              <button class="btn btn-danger btn-reject action-button reject" @click="rejectUser(user.id)">
                Reject
              </button>
              <button class="btn btn-info btn-view action-button view" @click="viewUserDetails(user)">
                View
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- User Details Modal -->
    <div v-if="showUserDetails" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeUserDetails">&times;</span>
        <h2>User Details</h2>
        <p>
          <strong>Name:</strong> {{ selectedUser.first_name }}
          {{ selectedUser.last_name }}
        </p>
        <p><strong>Phone:</strong> {{ selectedUser.phone }}</p>
        <p><strong>Address:</strong> {{ selectedUser.address }}</p>
        <p><strong>Zip:</strong> {{ selectedUser.zip_code }}</p>
        <p><strong>Requested At:</strong> {{ selectedUser.request_date }}</p>
        <div v-if="selectedUser.role === 'PROFESSIONAL'">
          <p><strong>Service Type:</strong> {{ selectedUser.service_type }}</p>
          <p>
            <strong>Experience:</strong>
            {{ selectedUser.experience_years }} years
          </p>
          <p>
            <strong>Portfolio:</strong>
            <button @click="downloadPortfolio(selectedUser.portfolio_link)">
              View Portfolio
            </button>
          </p>
          <p><strong>Rating:</strong> {{ selectedUser.average_rating }}</p>
        </div>
        <button class="btn-cancel" @click="closeUserDetails">Close</button>
      </div>
    </div>

    <!-- Manage Professionals & Customers -->
    <section class="dashboard-section">
      <h2><i class="fas fa-cogs"></i> Manage Users</h2>
      <table class="styled-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Role</th>
            <th>Zip</th>
            <th>Active</th>
            <th>Blocked</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in managedUsers" :key="item.id">
            <td>{{ item.name }}</td>
            <td>{{ item.role }}</td>
            <td>{{ item.zip_code }}</td>
            <td>
              <span v-if="item.is_active" class="status active">Active</span>
              <span v-else class="status inactive">Inactive</span>
            </td>
            <td>
              <span v-if="item.is_blocked" class="status blocked">Yes</span>
              <span v-else class="status unblocked">No</span>
            </td>
            <td>
              <button :class="item.is_active ? 'deactivate' : 'activate'" @click="toggleActive(item.user_id)">
                {{ item.is_active ? "Deactivate" : "Activate" }}
              </button>
              <button :class="item.is_blocked ? 'unblock' : 'block'" v-if="item.is_blocked"
                @click="unblockUser(item.user_id)">
                Unblock
              </button>
              <button v-else @click="blockUser(item.user_id)">Block</button>
            </td>
          </tr>
        </tbody>
      </table>
    </section>

    <!-- Manage Services -->
    <section class="dashboard-section">
      <h2><i class="fas fa-tools"></i> Services</h2>

      <button class="create-service-btn" @click="goToCreateService">
        + Create Service
      </button>
      <table class="styled-table" v-if="services.length">
        <thead>
          <tr>
            <th>Name</th>
            <th>Description</th>
            <th>Category</th>
            <th>Price</th>
            <th>Created At</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="service in services" :key="service.id">
            <td>{{ service.title }}</td>
            <td>{{ service.description }}</td>
            <td>{{ service.category }}</td>
            <td>${{ service.price }}</td>
            <td>{{ service.created_at }}</td>
            <td>
              <button class="update" @click="editService(service)">
                Update
              </button>
              <button class="delete" @click="deleteService(service.id)">
                Delete
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No services available.</p>
    </section>

    <!-- Edit Service Modal -->
    <div v-if="showEditModal" class="modal">
      <div class="modal-content">
        <span class="close" @click="closeEditModal">&times;</span>
        <h2>Edit Service</h2>
        <form @submit.prevent="updateService">
          <div>
            <label for="edit-title">Name:</label>
            <select v-model="editSelectedTitle" @change="autoFillEditCategory" required>
              <option value="" disabled>Select a Service</option>
              <option v-for="svc in predefinedServices" :key="svc.title" :value="svc.title">
                {{ svc.title }}
              </option>
            </select>
          </div>
          <div>
            <label for="edit-description">Description:</label>
            <textarea id="edit-description" v-model="editServiceData.description"></textarea>
          </div>
          <div>
            <label for="edit-category">Category:</label>
            <input type="text" v-model="editSelectedCategory" required />
          </div>
          <div>
            <label for="edit-price">Price:</label>
            <input type="number" step="0.01" id="edit-price" v-model="editServiceData.price" />
          </div>
          <button type="submit">Update</button>
        </form>
      </div>
    </div>

    <!-- Service Requests -->
    <section class="dashboard-section">
      <h2>Service Requests</h2>
      <table class="styled-table" v-if="serviceRequests && serviceRequests.length">
        <thead>
          <tr>
            <th>Request ID</th>
            <th>Customer</th>
            <th>Professional</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="req in serviceRequests" :key="req.id">
            <td>REQ-{{ req.id.toString().padStart(4, "0") }}</td>
            <td>{{ req.customer_name || "N/A" }}</td>
            <td>{{ req.professional_name || "N/A" }}</td>
            <td>
              <span :class="['status', statusClass(req.status)]">
                {{ displayStatus(req.status) }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else>No service requests available.</p>
    </section>

    <div class="admin-tip text-center mt-4">
      <small>💡 Tip: Keep your professionals list fresh and active!</small>
    </div>

  </div>
</template>

<script>
import axios from "axios";

export default {
  name: "AdminDashboardServiceRequests",
  name: "AdminSummary",
  data() {
    return {
      isSidebarCollapsed: false,
      pendingUsers: [],
      managedUsers: [],
      totalUsers: 0,
      totalProfessionals: 0,
      pendingRequests: 0,
      totalRevenue: 0,
      showUserDetails: false,
      selectedUser: {},
      services: [],
      serviceRequests: [],
      showEditModal: false,
      editServiceData: {},
      editSelectedTitle: "",
      editSelectedCategory: "",
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
    showNotification(message, type = "info", duration = 3000) {
      this.notification = message;
      this.notificationType = type;
      setTimeout(() => {
        this.notification = "";
        this.notificationType = "";
      }, duration);
    },
    toggleSidebar() {
      this.isSidebarCollapsed = !this.isSidebarCollapsed;
    },
    fetchPendingUsers() {
      const roles = ["CUSTOMER", "PROFESSIONAL"];
      this.pendingUsers = []; // Clear previous data

      roles.forEach((role) => {
        axios
          .get("http://127.0.0.1:5000/api/admin/pending_users", {
            params: { role: role },
          })
          .then((response) => {
            console.log(`Pending Users (${role}):`, response.data);
            // Merge results from both roles
            this.pendingUsers = [...this.pendingUsers, ...response.data];
          })
          .catch((error) =>
            console.error(`Error fetching pending ${role}s:`, error)
          );
      });
    },
    autoFillEditCategory() {
      const selected = this.predefinedServices.find(
        (svc) => svc.title === this.editSelectedTitle
      );
      this.editSelectedCategory = selected ? selected.category : "";
    },
    fetchManagedUsers() {
      axios
        .get("http://127.0.0.1:5000/api/admin/manage_users")
        .then((response) => {
          this.managedUsers = response.data;
        })
        .catch((err) => console.error("Error fetching managed users:", err));
    },
    blockUser(userId) {
      axios
        .post(`http://127.0.0.1:5000/api/admin/block_user/${userId}`)
        .then(() => {
          this.fetchManagedUsers();
        })
        .catch((err) => console.error("Error blocking user:", err));
    },
    unblockUser(userId) {
      axios
        .post(`http://127.0.0.1:5000/api/admin/unblock_user/${userId}`)
        .then(() => {
          this.fetchManagedUsers();
        })
        .catch((err) => console.error("Error unblocking user:", err));
    },
    approveUser(userId) {
      axios
        .post(`http://127.0.0.1:5000/api/admin/approve_user/${userId}`)
        .then(() => this.fetchPendingUsers())
        .catch((error) => console.error("Error approving user:", error));
    },
    rejectUser(userId) {
      axios
        .post(`http://127.0.0.1:5000/api/admin/reject_user/${userId}`)
        .then(() => this.fetchPendingUsers())
        .catch((error) => console.error("Error rejecting user:", error));
    },
    toggleActive(userId) {
      axios
        .post(`http://127.0.0.1:5000/api/admin/toggle_active/${userId}`)
        .then(() => this.fetchManagedUsers())
        .catch((err) => console.error("Error toggling active state:", err));
    },
    viewUserDetails(user) {
      console.log('Selected user:', user);
      this.selectedUser = user;
      this.showUserDetails = true;
    },
    closeUserDetails() {
      this.showUserDetails = false;
      this.selectedUser = {};
    },
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

    downloadReport() {
      const token = localStorage.getItem("token");

      // Triggering the asynchronous export job
      fetch("http://localhost:5000/api/export-closed-service-requests", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      })
        .then((response) => response.json())
        .then((data) => {
          const jobId = data.jobId;
          alert("Export job started. Please wait...");

          // Polling the status endpoint every second
          const interval = setInterval(() => {
            fetch(`http://localhost:5000/api/export-status?jobId=${jobId}`, {
              headers: {
                "Content-Type": "application/json",
                Authorization: `Bearer ${token}`,
              },
            })
              .then((response) => response.json())
              .then((statusData) => {
                if (statusData.status === "SUCCESS") {
                  clearInterval(interval);
                  alert("Export completed! Your CSV is ready for download.");

                  // Instead of a redirecting, fetching the file with the token and downloading it programmatically.
                  fetch("http://localhost:5000" + statusData.downloadUrl, {
                    method: "GET",
                    headers: {
                      "Content-Type": "application/json",
                      Authorization: `Bearer ${token}`,
                    },
                  })
                    .then((response) => {
                      if (!response.ok) {
                        throw new Error("Download request failed");
                      }
                      return response.blob();
                    })
                    .then((blob) => {
                      const url = window.URL.createObjectURL(blob);
                      const link = document.createElement("a");
                      link.href = url;
                      link.download = `report_${jobId}.csv`;
                      document.body.appendChild(link);
                      link.click();
                      link.remove();
                      setTimeout(() => window.URL.revokeObjectURL(url), 1000);
                    })
                    .catch((err) => {
                      console.error("Error downloading CSV:", err);
                      alert("Failed to download report.");
                    });
                } else if (statusData.status === "failed") {
                  clearInterval(interval);
                  alert("Export job failed: " + statusData.error);
                }
              })
              .catch((err) => {
                console.error("Error fetching job status:", err);
                clearInterval(interval);
              });
          }, 1000);
        });
    },

    goToCreateService() {
      this.$router.push("/create-service");
    },
    fetchServices() {
      axios
        .get("http://127.0.0.1:5000/api/admin/services", {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        })
        .then((response) => {
          this.services = response.data;
        })
        .catch((err) => console.error("Error fetching services:", err));
    },
    deleteService(serviceId) {
      axios
        .delete(`http://127.0.0.1:5000/api/admin/services/${serviceId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem("token")}` },
        })
        .then(() => {
          this.fetchServices();
        })
        .catch((err) => console.error("Error deleting service:", err));
    },
    editService(service) {
      console.log('Editing service:', service);
      this.editServiceData = { ...service };
      this.editSelectedTitle = service.title;
      this.editSelectedCategory = service.category;
      this.showEditModal = true;
    },
    closeEditModal() {
      this.showEditModal = false;
      this.editServiceData = {};
    },
    updateService() {
      this.editServiceData.title = this.editSelectedTitle;
      this.editServiceData.category = this.editSelectedCategory;

      axios
        .put(
          `http://127.0.0.1:5000/api/admin/services/${this.editServiceData.id}`,
          this.editServiceData,
          {
            headers: {
              Authorization: `Bearer ${localStorage.getItem("token")}`,
            },
          }
        )
        .then(() => {
          this.fetchServices();
          this.closeEditModal();
        })
        .catch((err) => console.error("Error updating service:", err));
    },
    displayStatus(status) {
      if (status && status.toUpperCase() === "REQUESTED") return "PENDING";
      return status;
    },
    statusClass(status) {
      const s = status ? status.toUpperCase() : "";
      if (s === "REQUESTED") return "pending";
      if (s === "IN_PROGRESS") return "in-progress";
      if (s === "ACCEPTED") return "accepted";
      if (s === "WORK_DONE") return "work-done";
      if (s === "COMPLETED") return "completed";
      return "";
    },
    // Fetching the service requests from the backend API.
    async fetchServiceRequests() {
      const token = localStorage.getItem("token");
      if (!token) {
        console.error("Missing authorization token.");
        return;
      }
      try {
        const response = await fetch("http://localhost:5000/get_requests", {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });
        if (!response.ok) {
          console.error("Error fetching service requests:", response.status);
          return;
        }
        const data = await response.json();
        console.log("Fetched service requests:", data);
        this.serviceRequests = data;
      } catch (error) {
        console.error("Error in fetchServiceRequests:", error);
      }
    },
    async fetchAdminSummary() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.showNotification("Please log in.", "danger");
        return;
      }
      try {
        const response = await fetch(
          "http://localhost:5000/api/admin/summary",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) {
          this.showNotification("Error fetching admin summary.", "danger");
          return;
        }
        const data = await response.json();
        this.totalUsers = data.total_users;
        this.totalProfessionals = data.total_professionals;
        this.pendingRequests = data.pending_requests;
        this.totalRevenue = data.total_revenue;
      } catch (error) {
        console.error("Error fetching admin summary:", error);
        this.showNotification("An error occurred.", "danger");
      }
    },
  },
  mounted() {
    this.fetchPendingUsers();
    this.fetchManagedUsers();
    this.fetchServices();
    this.fetchServiceRequests();
    this.fetchAdminSummary();
  },
};
</script>

<style src="@/assets/css/AdminDashboard.css"></style>
