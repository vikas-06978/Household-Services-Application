<template>
  <div class="customer-dashboard container-fluid">
    <div class="row">
      <!-- Sidebar Navigation -->
      <div class="col-md-3 sidebar">
        <div class="dashboard-menu welcome-banner">
          <h2>Customer Dashboard</h2>
          <img src="@/assets/illustrations/customer-welcome.svg" class="welcome-img" alt="Welcome" />
          <p>Ready to book your next service? Explore top professionals!</p>
          <ul class="list-group">
            <li class="list-group-item" :class="{ active: activeTab === 'services' }" @click="activeTab = 'services'">
              Available Services
            </li>
            <li class="list-group-item" :class="{ active: activeTab === 'pending' }" @click="activeTab = 'pending'">
              Pending Requests
            </li>
            <li class="list-group-item" :class="{ active: activeTab === 'accepted' }" @click="activeTab = 'accepted'">
              Accepted Requests
            </li>
            <li class="list-group-item" :class="{ active: activeTab === 'inProgress' }"
              @click="activeTab = 'inProgress'">
              Work In Progress
            </li>
            <li class="list-group-item" :class="{ active: activeTab === 'done' }" @click="activeTab = 'done'">
              Work Done
            </li>
            <li class="list-group-item" :class="{ active: activeTab === 'completed' }" @click="activeTab = 'completed'">
              Completed Requests
            </li>

            <li class="list-group-item" :class="{ active: activeTab === 'myRatings' }" @click="activeTab = 'myRatings'">
              My Ratings & Reviews
            </li>

            <li class="list-group-item" v-if="subscriptionStatus === 'active'"
              :class="{ active: activeTab === 'mysubscription' }" @click="activeTab = 'mysubscription'">
              👑 My Subscription
            </li>
          </ul>

          <div v-if="subscriptionStatus === 'active'" class="mt-3 px-2">
            <button class="btn btn-success btn-block" @click="exportServiceHistory">
              📄 Export Service History
            </button>
          </div>

          <div class="mt-4 text-center">
            <router-link to="/subscription" class="btn btn-outline-primary btn-block">
              👑 Manage Subscription
            </router-link>
          </div>
        </div>
      </div>

      <!-- Main Content Area -->
      <div class="col-md-9 main-content">
        <!-- Global Notification -->
        <div v-if="notification" :class="`alert alert-${notificationType}`" role="alert">
          {{ notification }}
        </div>


        <!-- Show banner ONLY in 'subscription' tab -->
        <div v-if="
          activeTab === 'mysubscription' && subscriptionStatus === 'active'
        " class="bg-white shadow rounded p-4 my-4 subscription-section" style="border-left: 6px solid #007bff">
          <h2 class="text-center text-primary mb-3">
            👑 Your Premium Membership
          </h2>

          <!-- Validity Info -->
          <div class="text-center mb-4">
            <span class="badge bg-info text-dark px-4 py-2 fs-6 premium-badge">
              Active Until: {{ subscriptionExpiry }}
            </span>
            <p class="mt-2 text-muted">
              Enjoy all premium features below until your plan expires!
            </p>
          </div>

          <!-- What You Get -->
          <div class="mb-4">
            <h5 class="text-success mb-3"> What You Get</h5>
            <div class="row g-3">
              <div class="col-md-6">
                <div class="p-3 border rounded bg-light premium-feature">
                  Export service history as PDF
                </div>
              </div>
              <div class="col-md-6">
                <div class="p-3 border rounded bg-light premium-feature">
                  Early access to professionals
                </div>
              </div>
              <div class="col-md-6">
                <div class="p-3 border rounded bg-light premium-feature">
                  Priority customer support
                </div>
              </div>
              <div class="col-md-6">
                <div class="p-3 border rounded bg-light premium-feature">
                  Contact assigned professionals
                </div>
              </div>
              <div class="col-12">
                <div class="p-3 border rounded bg-light premium-feature">
                  Monthly booking insights (coming soon)
                </div>
              </div>
            </div>
          </div>

          <!-- Usage Summary -->
          <div class="mb-4">
            <h5 class="text-primary mb-3"> Your Usage</h5>
            <div class="row text-center">
              <div class="col-md-4">
                <div class="bg-white border rounded shadow-sm p-3 usage-card">
                  <h6 class="text-muted">Bookings Made</h6>
                  <p class="fs-4 text-success mb-0">{{ totalBookings || 0 }}</p>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-white border rounded shadow-sm p-3 usage-card">
                  <h6 class="text-muted">PDF Exports</h6>
                  <p class="fs-4 text-info mb-0">{{ pdfExports || 0 }}</p>
                </div>
              </div>
              <div class="col-md-4">
                <div class="bg-white border rounded shadow-sm p-3 usage-card">
                  <h6 class="text-muted">Priority Requests</h6>
                  <p class="fs-4 text-warning mb-0">
                    {{ priorityRequests || 0 }}
                  </p>
                </div>
              </div>
            </div>
          </div>

          <!-- Testimonial -->
          <div class="alert alert-light border-start border-4 border-primary testimonial-box">

            <em>"I’ve never had to wait again! Premium is totally worth it." —
              Verified Premium User</em>
          </div>

          <!-- Actions -->
          <div class="text-center mt-4">
            <button class="btn btn-warning px-4 me-2 subscription-btn renew me-3">
              Renew Subscription
            </button>
            <router-link to="/subscription" class="btn btn-outline-primary px-4 subscription-btn manage">
              ⚙️ Manage Plan
            </router-link>
          </div>
        </div>

        <!-- Subscription Page View -->
        <div v-if="activeTab === 'subscription'">
          <SubscriptionComponent />
        </div>

        <!-- Filters for Services -->
        <div class="filters" v-if="activeTab != 'mysubscription'">
          <input v-model="searchName" :placeholder="getSearchPlaceholder" class="search-input"
            @input="filterServices" />

          <!-- New Price Order Dropdown -->
          <label class="order-label" v-if="activeTab !== 'myRatings'">
            Order by Price:
            <select v-model="priceOrder" @change="filterServices" class="order-dropdown">
              <option value="asc">Low to High</option>
              <option value="desc">High to Low</option>
            </select>
          </label>

          <label class="order-label" v-if="activeTab === 'myRatings'">
            Order by Rating:
            <select v-model="ratingOrder" class="order-dropdown form-select">
              <option value="desc">High to Low</option>
              <option value="asc">Low to High</option>
            </select>
          </label>

          <button @click="clearFilters" class="btn btn-secondary">
            Clear Filters
          </button>
        </div>

        <!-- Available Services Section -->
        <div v-if="activeTab === 'services'">
          <h3>Available Services</h3>
          <table class="table table-hover table-bordered">
            <thead>
              <tr>
                <th>Service Name</th>
                <th>Description</th>
                <th>Price</th>
                <th>Professionals</th>
                <th>Desired Date</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in filteredServices" :key="service.id">
                <td>{{ service.title }}</td>
                <td>{{ service.description }}</td>
                <td>{{ service.price }}</td>
                <td>
                  <select class="form-select" v-model="selectedPro[service.id]">
                    <option disabled value="">Choose a Professional</option>
                    <option v-for="pro in professionalsFor(service)" :key="pro.id" :value="pro.id">
                      {{ pro.name ? pro.name : "Unnamed Professional" }} ({{
                        pro.experience_years || 0
                      }}
                      yrs)
                    </option>
                  </select>
                  <div v-if="!professionalsFor(service).length" class="text-danger professionals-box">
                    No professionals available
                  </div>
                </td>
                <td>
                  <input type="date" v-model="desiredDates[service.id]" :min="today" />
                </td>
                <td>
                  <button class="btn btn-primary" @click="sendRequest(service.id)" :disabled="!selectedPro[service.id] || !desiredDates[service.id]
                    ">
                    Send Request
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pending Requests Section -->
        <div v-if="activeTab === 'pending'">
          <h3>Pending Requests</h3>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Service</th>
                <th>Professional</th>
                <th>Price</th>
                <th>Desired Date</th>
                <th>Requested On</th>
                <th>Status</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in getFilteredPendingRequests()" :key="req.id">
                <td>{{ req.service_title || "N/A" }}</td>
                <td>
                  {{ req.professional_name || req.professional?.name || "N/A" }}
                </td>
                <td>{{ req.service_price || "N/A" }}</td>
                <td>{{ formatDate(req.desired_service_date) }}</td>
                <td>{{ formatDate(req.request_date) }}</td>
                <td>{{ displayStatus(req.status) }}</td>
                <td>
                  <button class="btn btn-warning" @click="openEditDateModal(req)">
                    Edit Date
                  </button>
                  <button class="btn btn-danger" @click="cancelRequest(req.id)">
                    Cancel
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!--Edit Model-->
        <div v-if="showEditDateModal" class="modal">
          <div class="modal-content">
            <span class="close" @click="closeEditDateModal">&times;</span>
            <h2>Edit Service Date</h2>
            <p>Service: {{ editingRequest.service_title }}</p>
            <p>
              <input type="date" v-model="editingDate" :min="today" />
            </p>
            <button @click="updateRequestDate(editingRequest.id)">Save</button>
          </div>
        </div>

        <!-- Accepted Requests Section -->
        <div v-if="activeTab === 'accepted'">
          <h3>Accepted Requests</h3>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Service</th>
                <th>Professional</th>
                <th>Price</th>
                <th>Desired Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in getFilteredAcceptedRequests()" :key="req.id">
                <td>{{ req.service_title || "N/A" }}</td>
                <td>{{ req.professional_name || "N/A" }}</td>
                <td>{{ req.service_price || "N/A" }}</td>
                <td>{{ formatDate(req.desired_service_date) }}</td>
                <td>{{ req.status || "N/A" }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Work In Progress Section -->
        <div v-if="activeTab === 'inProgress'">
          <h3>Work In Progress</h3>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Service</th>
                <th>Professional</th>
                <th>Price</th>
                <th>Desired Date</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in getFilteredInProgressRequests()" :key="req.id">
                <td>{{ req.service_title || "N/A" }}</td>
                <td>{{ req.professional_name || "N/A" }}</td>
                <td>{{ req.service_price || "N/A" }}</td>
                <td>{{ formatDate(req.desired_service_date) }}</td>
                <td>{{ req.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Work Done Section -->
        <div v-if="activeTab === 'done'">
          <h3>Work Done</h3>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Request ID</th>
                <th>Service</th>
                <th>Price</th>
                <th>Desired Date</th>
                <th>Status</th>
                <th>Payment</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in getFilteredWorkDoneRequests()" :key="req.id">
                <td>{{ req.id }}</td>
                <td>{{ req.service_title || "N/A" }}</td>
                <td>{{ req.service_price || "N/A" }}</td>
                <td>{{ formatDate(req.desired_service_date) }}</td>
                <td>{{ req.status }}</td>
                <td>
                  <button class="btn btn-primary" @click="processPayment(req.id)">
                    Pay Now
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Completed Requests Section -->
        <div v-if="activeTab === 'completed'">
          <h3>Completed Requests</h3>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Service</th>
                <th>Professional</th>
                <th>Price</th>
                <th>Requested On</th>
                <th>Completed On</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="req in getFilteredCompletedRequests()" :key="req.id">
                <td>{{ req.service_title || "N/A" }}</td>
                <td>{{ req.professional_name || "N/A" }}</td>
                <td>{{ req.service_price || "N/A" }}</td>
                <td>{{ formatDate(req.request_date) }}</td>
                <td>{{ formatDate(req.completion_date) || "N/A" }}</td>
                <td>{{ req.status }}</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- My Ratings & Reviews Section -->
        <div v-if="activeTab === 'myRatings'">
          <h3>My Ratings & Reviews</h3>
          <table class="table table-bordered">
            <thead>
              <tr>
                <th>Request ID</th>
                <th>Professional</th>
                <th>Rating</th>
                <th>Remarks</th>
                <th>Completed On</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="review in getFilteredMyRatingReviews()" :key="review.request_id">
                <td>{{ review.request_id }}</td>
                <td>{{ review.professional_name || "N/A" }}</td>
                <td>{{ review.rating }}</td>
                <td>{{ review.remarks }}</td>
                <td>{{ formatDate(review.completed_on) }}</td>
                <td>
                  <button v-if="review.editable" class="btn btn-warning" @click="openEditReviewModal(review)">
                    Edit
                  </button>
                </td>
              </tr>
            </tbody>
          </table>

          <!-- Edit Modal -->
          <div v-if="showEditReviewModal" class="modal-overlay">
            <div class="modal-content">
              <h3>Edit Review</h3>
              <p>Request ID: {{ editingReview.request_id }}</p>
              <label>
                Rating (1-5):
                <input type="number" v-model.number="editingRating" min="1" max="5" step="0.5" />
              </label>
              <br />
              <label>
                Remarks:
                <textarea v-model="editingRemarks"></textarea>
              </label>
              <br />
              <div class="modal-actions">
                <button @click="updateReview" class="btn btn-success ">
                  Save
                </button>
                <button @click="closeEditReviewModal" class="btn btn-secondary">
                  Cancel
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- Alert for Max Request Limit -->
        <div v-if="Object.keys(maxRequestsReached).length" class="alert alert-warning mt-3">
          <strong>Alert:</strong> Some professionals have reached the maximum
          number of active requests.
        </div>
      </div>
    </div>
    <div class="quick-tips p-3 rounded mt-4">
      <h6>✨ Pro Tips:</h6>
      <ul>
        <li>Compare professionals based on experience.</li>
        <li>Track status in "Work In Progress".</li>
        <li>Submit reviews after service is done.</li>
      </ul>
    </div>
  </div>
</template>

<script>
import axios from "axios";
import SubscriptionComponent from "@/components/Subscription.vue";

export default {
  name: "CustomerDashboard",
  components: {
    SubscriptionComponent,
  },

  data() {
    return {
      activeTab: "services",
      notification: "",
      notificationType: "info",
      availableServices: [], // Services fetched from API
      selectedPro: {},
      activeProRequests: {},
      pendingRequests: [],
      acceptedRequests: [],
      inProgressRequests: [],
      workDoneRequests: [],
      completedRequests: [],
      serviceLookup: {},
      maxRequestLimit: 3,
      maxRequestsReached: {},
      services: [], // full list of services from the backend
      filteredServices: [], // Currently filtered list
      searchName: "",
      priceOrder: "asc",
      desiredDates: {},
      showEditReviewModal: false,
      editingDate: "",
      requests: [],
      reviews: [],
      myRatings: [],
      showEditDateModal: false,
      editingRequest: {}, // The request currently being edited
      editingRating: null, // Temporary field for rating input
      editingRemarks: "",
      ratingOrder: "desc",
      subscriptionStatus: "none",
    };
  },
  computed: {
    subscriptionStatus() {
      return localStorage.getItem("subscriptionStatus") || "inactive";
    },
    today() {
      const d = new Date();
      return d.toISOString().split("T")[0];
    },
    getSearchPlaceholder() {
      switch (this.activeTab) {
        case "services":
          return "Filter by service or Professional ...";
        case "myRatings":
          return "Filter by professional, rating or remarks...";
        case "pending":
        case "accepted":
        case "inProgress":
        case "workDone":
        case "completed":
          return "Filter your service, Professional or Price...";
        default:
          return "Service or Price...";
      }
    },
  },
  mounted() {

    this.customerId = localStorage.getItem("customerId");
    axios
      .get("/api/public/services")
      .then((response) => {
        this.services = response.data;
        this.filterServices(); // Initializing filteredServices
      })
      .catch((error) => {
        console.error("Error fetching services:", error);
      });
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

    filterRequests(requestArray) {
      const nameQuery = this.searchName.toLowerCase().trim();

      let filtered = requestArray.filter((req) => {
        if (!nameQuery) return true;

        return (
          (req.service_title &&
            req.service_title.toLowerCase().includes(nameQuery)) ||
          (req.professional_name &&
            req.professional_name.toLowerCase().includes(nameQuery)) ||
          (req.service_price &&
            String(req.service_price).toLowerCase().includes(nameQuery)) ||
          (req.desired_date &&
            req.desired_date.toLowerCase().includes(nameQuery)) ||
          (req.status && req.status.toLowerCase().includes(nameQuery))
        );
      });

      // Sorting by service_price if available
      if (this.priceOrder === "asc") {
        filtered.sort(
          (a, b) => (a.service_price || 0) - (b.service_price || 0)
        );
      } else if (this.priceOrder === "desc") {
        filtered.sort(
          (a, b) => (b.service_price || 0) - (a.service_price || 0)
        );
      }
      return filtered;
    },

    getFilteredPendingRequests() {
      return this.filterRequests(this.pendingRequests);
    },
    getFilteredAcceptedRequests() {
      return this.filterRequests(this.acceptedRequests);
    },
    getFilteredInProgressRequests() {
      return this.filterRequests(this.inProgressRequests);
    },
    getFilteredWorkDoneRequests() {
      return this.filterRequests(this.workDoneRequests);
    },
    getFilteredCompletedRequests() {
      return this.filterRequests(this.completedRequests);
    },
    getFilteredMyRatingReviews() {
      const query = this.searchName.toLowerCase().trim();

      let filtered = this.myRatings.filter((review) => {
        return (
          (review.professional_name &&
            review.professional_name.toLowerCase().includes(query)) ||
          (review.remarks && review.remarks.toLowerCase().includes(query)) ||
          String(review.rating).toLowerCase().includes(query)
        );
      });

      // Sorting by rating
      if (this.ratingOrder === "asc") {
        filtered.sort((a, b) => a.rating - b.rating);
      } else if (this.ratingOrder === "desc") {
        filtered.sort((a, b) => b.rating - a.rating);
      }

      return filtered;
    },

    // Filtering for Available Services
    filterServices() {
      const nameQuery = this.searchName.toLowerCase().trim();
      let filtered = this.services.filter((svc) => {
        return !nameQuery || svc.title.toLowerCase().includes(nameQuery);
      });

      if (this.priceOrder === "asc") {
        filtered.sort((a, b) => a.price - b.price);
      } else if (this.priceOrder === "desc") {
        filtered.sort((a, b) => b.price - a.price);
      }

      this.filteredServices = filtered;
    },

    clearFilters() {
      this.searchName = "";
      this.priceOrder = "asc";
      this.ratingOrder = "desc";
      this.filterServices();

    },


    formatDate(isoString) {
      if (!isoString) return "N/A";
      return new Date(isoString).toLocaleString();
    },
    formatDateOnly(dateString) {
      if (!dateString) return "";
      const d = new Date(dateString);
      const year = d.getFullYear();
      const month = String(d.getMonth() + 1).padStart(2, "0");
      const day = String(d.getDate()).padStart(2, "0");
      return `${year}-${month}-${day}`;
    },

    async fetchServices() {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          "http://localhost:5000/api/public/services",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (response.status === 403) {
          console.error("Access forbidden: Missing or invalid token.");
          this.showNotification(
            "You are not authorized to view this data.",
            "danger"
          );
          return;
        }
        const data = await response.json();
        this.availableServices = data;
        // Storing in services for filtering
        this.services = data;
        this.filterServices(); // Initializing filteredServices
        console.log("Fetched services:", this.availableServices);
        console.log("Fetched services:", this.availableServices);
      } catch (error) {
        console.error("Error fetching services:", error);
      }
    },
    professionalsFor(service) {
      return service.professionals || [];
    },
    async sendRequest(serviceId) {
      const professionalId = this.selectedPro[serviceId];
      const desiredDate = this.desiredDates[serviceId];

      if (!professionalId) {
        alert("Please select a professional.");
        return;
      }

      if (!desiredDate) {
        alert("Please select a desired date.");
        return;
      }

      const token = localStorage.getItem("token");
      if (!token) {
        alert("You are not logged in. Please log in first.");
        return;
      }

      // Retrieving the dynamic customer ID from localStorage
      const storedCustomerId = localStorage.getItem("customerId");
      const dateForService = this.desiredDates[serviceId] || null;
      console.log("Retrieved customerId:", storedCustomerId);
      const customerId = storedCustomerId
        ? parseInt(storedCustomerId, 10)
        : null;
      if (!customerId) {
        alert("Customer ID not found. Please log in properly.");
        return;
      }

      try {
        const response = await fetch("http://localhost:5000/request_service", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            customer_id: customerId, // Using dynamic customer ID 
            professional_id: this.selectedPro[serviceId],
            service_id: serviceId,
            desired_service_date: dateForService,
          }),
        });

        const data = await response.json();
        console.log("API Response:", data);

        if (response.ok) {
          this.showNotification("Request sent successfully!", "success");
          this.fetchPendingRequests(); // Refreshing pending requests
        } else {
          this.showNotification(data.error || "Failed to send request.", "danger");
        }
      } catch (error) {
        console.error("Error sending request:", error);
        this.showNotification("Server error. Please try again.", "danger")
      }
    },
    async fetchPendingRequests() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("Missing authorization token.");
          this.showNotification(
            "Please log in to view pending requests.",
            "danger"
          );
          return;
        }

        const response = await fetch(
          `http://localhost:5000/get_requests?customer_id=${this.customerId}&status=REQUESTED`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 403) {
          console.error("Access forbidden: Missing or invalid token.");
          this.showNotification(
            "You are not authorized to view this data.",
            "danger"
          );
          return;
        }

        const data = await response.json();
        console.log("Pending Requests Data:", data);

        this.pendingRequests = data;
      } catch (error) {
        console.error("Error fetching pending requests:", error);
      }
    },
    openEditDateModal(request) {
      this.editingRequest = request;
      if (request.desired_service_date) {
        const dt = new Date(request.desired_service_date);
        this.editingDate = dt.toISOString().split("T")[0];
      } else {
        this.editingDate = "";
      }
      this.showEditDateModal = true;
    },
    closeEditDateModal() {
      this.showEditDateModal = false;
      this.editingRequest = {};
      this.editingDate = "";
    },
    async updateRequestDate(requestId) {
      try {
        const token = localStorage.getItem("token");
        const response = await fetch(
          `http://localhost:5000/api/requests/${requestId}`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ desired_service_date: this.editingDate }),
          }
        );
        const data = await response.json();
        if (!response.ok)
          throw new Error(data.error || "Failed to update request date");

        alert("Request date updated successfully!");
        this.showEditModal = false;
        this.fetchPendingRequests();
      } catch (err) {
        console.error(err);
        alert("Error updating request date: " + err.message);
      }
    },

    async cancelRequest(requestId) {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          this.showNotification("Please log in to cancel requests.", "danger");
          return;
        }

        // Sending a DELETE request for the specific request id.
        const response = await fetch(
          `http://localhost:5000/api/requests/${requestId}`,
          {
            method: "DELETE",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();
        if (!response.ok) {
          throw new Error(data.error || "Cancellation failed.");
        }

        // Removeing the canceled request from the pending requests list.
        this.pendingRequests = this.pendingRequests.filter(
          (r) => r.id !== requestId
        );
        this.showNotification(data.message, "success");
      } catch (error) {
        this.showNotification(error.message, "danger");
      }
    },

    async fetchAcceptedRequests() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("Missing authorization token.");
          this.showNotification(
            "Please log in to view accepted requests.",
            "danger"
          );
          return;
        }

        const response = await fetch(
          `http://localhost:5000/get_requests?customer_id=${this.customerId}&status=ACCEPTED`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 403) {
          console.error("Access forbidden: Missing or invalid token.");
          this.showNotification(
            "You are not authorized to view this data.",
            "danger"
          );
          return;
        }

        const data = await response.json();
        console.log("Accepted Requests Data:", data);
        this.acceptedRequests = data;
      } catch (error) {
        console.error("Error fetching accepted requests:", error);
      }
    },
    async fetchInProgressRequests() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("Missing authorization token.");
          this.showNotification(
            "Please log in to view in-progress requests.",
            "danger"
          );
          return;
        }

        const response = await fetch(
          `http://localhost:5000/get_requests?customer_id=${this.customerId}&status=IN_PROGRESS`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 403) {
          console.error("Access forbidden: Missing or invalid token.");
          this.showNotification(
            "You are not authorized to view this data.",
            "danger"
          );
          return;
        }

        const data = await response.json();
        console.log("In-Progress Requests Data:", data);
        this.inProgressRequests = data;
      } catch (error) {
        console.error("Error fetching in-progress requests:", error);
      }
    },
    async fetchWorkDoneRequests() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("Missing authorization token.");
          this.showNotification(
            "Please log in to view work done requests.",
            "danger"
          );
          return;
        }

        const response = await fetch(
          `http://localhost:5000/get_requests?customer_id=${this.customerId}&status=WORK_DONE`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.status === 403) {
          console.error("Access forbidden: Missing or invalid token.");
          this.showNotification(
            "You are not authorized to view this data.",
            "danger"
          );
          return;
        }

        const data = await response.json();
        console.log("Work Done Requests Data:", data);
        this.workDoneRequests = data;
      } catch (error) {
        console.error("Error fetching work done requests:", error);
      }
    },
    async fetchCompletedRequests() {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error("Missing authorization token.");
          this.showNotification(
            "Please log in to view completed requests.",
            "danger"
          );
          return;
        }
        const response = await fetch(
          `http://localhost:5000/get_requests?customer_id=${this.customerId}&status=COMPLETED`,
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );
        if (response.status === 403) {
          console.error("Access forbidden: Missing or invalid token.");
          this.showNotification(
            "You are not authorized to view this data.",
            "danger"
          );
          return;
        }
        const data = await response.json();
        console.log("Completed Requests Data:", data);
        this.completedRequests = data;
      } catch (error) {
        console.error("Error fetching completed requests:", error);
      }
    },
    formatDate(dateStr) {
      const d = new Date(dateStr);
      return d.toLocaleDateString() + " " + d.toLocaleTimeString();
    },
    fetchRatingHistory() {
      const token = localStorage.getItem("token");
      axios
        .get("http://localhost:5000/customer/rating_history", {
          headers: { Authorization: `Bearer ${token}` },
        })
        .then((response) => {
          this.reviews = response.data;
        })
        .catch((err) => {
          console.error("Error fetching rating history:", err);
          alert("Unable to fetch rating history.");
        });
    },
    openEditReviewModal(review) {
      // Copying review data into editing fields
      this.editingReview = { ...review };
      this.editingRating = review.rating;
      this.editingRemarks = review.remarks;
      this.showEditReviewModal = true;
    },
    closeEditReviewModal() {
      this.showEditReviewModal = false;
      this.editingReview = {};
      this.editingRating = null;
      this.editingRemarks = "";
    },
    updateReview() {
      const token = localStorage.getItem("token");
      axios
        .post(
          `http://localhost:5000/customer/rate/${this.editingReview.request_id}`,
          {
            rating: this.editingRating,
            remarks: this.editingRemarks,
          },
          {
            headers: { Authorization: `Bearer ${token}` },
          }
        )
        .then((response) => {
          alert(response.data.message);
          this.closeEditReviewModal();
          this.fetchRatingHistory();
        })
        .catch((err) => {
          console.error("Error updating review:", err);
          if (err.response && err.response.data.error) {
            alert(err.response.data.error);
          } else {
            alert("Error updating review.");
          }
        });
    },
    fetchMyRatings() {
      const token = localStorage.getItem("token");
      axios
        .get("http://localhost:5000/customer/rating_history", {
          headers: { Authorization: `Bearer ${token}` },
        })
        .then((response) => {
          this.myRatings = response.data;
        })
        .catch((err) => {
          console.error("Error fetching rating history:", err);
          alert("Unable to fetch rating history.");
        });
    },
    formatDate(isoString) {
      if (!isoString) return "N/A";
      return new Date(isoString).toLocaleString("en-IN", {
        timeZone: "Asia/Kolkata",
      });
    },
    processPayment(requestId) {
      this.$router.push({ name: "Payment", params: { requestId } });
    },
    async fetchSubscriptionStatus() {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch(
          "http://localhost:5000/api/customer/subscription_status",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!res.ok) {
          console.error("Subscription status fetch failed.");
          throw new Error("Server error");
        }

        const data = await res.json();

        // Checking if expiry is in the past
        const expiry = new Date(data.subscription_expiry);
        const now = new Date();

        if (!data.subscription_expiry || expiry < now) {
          // Treating as inactive if expired or missing
          this.subscriptionStatus = "inactive";
          localStorage.setItem("subscriptionStatus", "inactive");
        } else {
          this.subscriptionStatus = "active";
          localStorage.setItem("subscriptionStatus", "active");
        }

        //  storing the expiry date too
        this.subscriptionExpiry = data.subscription_expiry;
        localStorage.setItem(
          "subscriptionExpiry",
          data.subscription_expiry || ""
        );
      } catch (err) {
        console.error("Failed to fetch subscription status:", err);
        this.subscriptionStatus = "inactive";
        localStorage.setItem("subscriptionStatus", "inactive");
      }
    },
    async cancelSubscription() {
      const confirmCancel = confirm(
        "Are you sure you want to cancel your subscription?"
      );
      if (!confirmCancel) return;

      const token = localStorage.getItem("token");
      try {
        const res = await fetch(
          "http://localhost:5000/api/customer/cancel_subscription",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await res.json();
        if (!res.ok) throw new Error(data.error || "Cancellation failed.");

        // Setting UI and localStorage
        localStorage.setItem("subscriptionStatus", "inactive");
        this.subscriptionStatus = "inactive";
        alert("Subscription cancelled. You're back to free mode.");
      } catch (err) {
        alert("Error cancelling subscription: " + err.message);
      }
    },

    async exportServiceHistory() {
      this.notification = "";
      this.notificationType = "";
      try {
        const token = localStorage.getItem("token");
        const customerId = localStorage.getItem("customerId");

        const response = await fetch(
          `http://localhost:5000/api/customer/export_service_history?customer_id=${customerId}`,
          {
            method: "GET",
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          const errorData = await response.json();

          if (response.status === 404 && errorData.error) {
            this.showNotification(errorData.error, "warning");
          } else {
            throw new Error(errorData.error || "Failed to export pdf");
          }
          return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = `Service_History_${customerId}.pdf`;
        a.click();
        window.URL.revokeObjectURL(url);
      } catch (err) {
        console.error("Export failed:", err);
        alert("Failed to export service history. Please try again.");
      }
    },

    displayStatus(rawStatus) {
      if (rawStatus === "REQUESTED") {
        return "PENDING";
      }
      return rawStatus;
    },
  },
  created() {
    this.customerId = localStorage.getItem("customerId");
    if (!this.customerId) {
      console.warn(
        "Customer ID not found in localStorage. Please log in properly."
      );
    }
    this.fetchServices();
    this.fetchPendingRequests();
    this.fetchAcceptedRequests();
    this.fetchInProgressRequests();
    this.fetchWorkDoneRequests();
    this.fetchCompletedRequests();
    this.fetchRatingHistory();
    this.fetchMyRatings();
    this.fetchSubscriptionStatus();
  },
};
</script>

<style src="@/assets/css/CustomerDashboard.css"></style>
