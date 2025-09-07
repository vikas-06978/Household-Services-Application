<template>
  <div class="professional-dashboard container">
    <!-- Header with Global Notification -->
    <div class="header text-center my-4">
      <h1 class="dashboard-title">Professional Dashboard</h1>
      <p class="subtitle">You’re part of 300+ professionals delivering trusted services.</p>
      <div v-if="notification" :class="`alert alert-${notificationType}`">
        {{ notification }}
      </div>
    </div>

    <!-- Top Tab Navigation -->
    <ul class="nav nav-tabs justify-content-center table-section">
      <li class="nav-item" @click="activeTab = 'new'">
        <a :class="['nav-link', { active: activeTab === 'new' }]" href="#">New Requests</a>
      </li>
      <li class="nav-item" @click="activeTab = 'accepted'">
        <a :class="['nav-link', { active: activeTab === 'accepted' }]" href="#">Accepted</a>
      </li>
      <li class="nav-item" @click="activeTab = 'inProgress'">
        <a :class="['nav-link', { active: activeTab === 'inProgress' }]" href="#">In Progress</a>
      </li>
      <li class="nav-item" @click="activeTab = 'done'">
        <a :class="['nav-link', { active: activeTab === 'done' }]" href="#">Work Done</a>
      </li>
      <li class="nav-item" @click="activeTab = 'completed'">
        <a :class="['nav-link', { active: activeTab === 'completed' }]" href="#">Completed</a>
      </li>
      <li class="nav-item" @click="activeTab = 'myReviews'">
        <a :class="['nav-link', { active: activeTab === 'myReviews' }]" href="#">My Reviews</a>
      </li>
    </ul>

    <!-- Tab Content -->
    <div class="tab-content mt-4">
      <!-- New Requests Tab -->
      <div v-if="activeTab === 'new'" class="tab-pane active ">
        <h3>New Service Requests</h3>
        <table class="table table-hover ">
          <thead>
            <tr>
              <th>Service</th>
              <th>Customer</th>
              <th>Price</th>
              <th>Desired Date</th>
              <th>Requested On</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in newRequests" :key="req.id">
              <td>{{ req.service_title || "N/A" }}</td>
              <td>{{ req.customer_name || "N/A" }}</td>
              <td>{{ req.service_price || "N/A" }}</td>
              <td>{{ formatDate(req.desired_service_date) }}</td>
              <td>{{ formatDate(req.request_date) }}</td>
              <td>{{ displayStatus(req.status) }}</td>

              <td>
                <button class="btn btn-success btn-sm" @click="acceptRequest(req.id)">
                  Accept
                </button>
                <button class="btn btn-danger btn-sm" @click="rejectRequest(req.id)">
                  Reject
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Accepted Requests Tab -->
      <div v-if="activeTab === 'accepted'" class="tab-pane active">
        <h3>Accepted Requests</h3>
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Service</th>
              <th>Customer</th>
              <th>Desired Date</th>
              <th>Status</th>
              <th>Progress</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in acceptedRequests" :key="req.id">
              <td>{{ req.service_title || "N/A" }}</td>
              <td>{{ req.customer_name || "N/A" }}</td>
              <td>{{ formatDate(req.desired_service_date) }}</td>
              <td>{{ req.status }}</td>
              <td>
                <button class="btn btn-info btn-sm" @click="markInProgress(req.id)">
                  Mark as In Progress
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- In Progress Requests Tab -->
      <div v-if="activeTab === 'inProgress'" class="tab-pane active">
        <h3>Work In Progress</h3>
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Service</th>
              <th>Customer</th>
              <th>Desired Date</th>
              <th>Status</th>
              <th>Complete</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in inProgressRequests" :key="req.id">
              <td>{{ req.service_title || "N/A" }}</td>
              <td>{{ req.customer_name || "N/A" }}</td>
              <td>{{ formatDate(req.desired_service_date) }}</td>
              <td>{{ req.status }}</td>
              <td>
                <button class="btn btn-success btn-sm" @click="markWorkDone(req.id)">
                  Mark Work Done
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Work Done Requests Tab -->
      <div v-if="activeTab === 'done'" class="tab-pane active">
        <h3>Work Done</h3>
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Service</th>
              <th>Customer</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in workDoneRequests" :key="req.id">
              <td>{{ req.service_title || "N/A" }}</td>
              <td>{{ req.customer_name || "N/A" }}</td>
              <td>{{ req.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Completed Requests Tab -->
      <div v-if="activeTab === 'completed'" class="tab-pane active">
        <h3>Completed Requests</h3>
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Service</th>
              <th>Customer</th>
              <th>Completed On</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="req in completedRequests" :key="req.id">
              <td>{{ req.service_title || "N/A" }}</td>
              <td>{{ req.customer_name || "N/A" }}</td>
              <td>{{ formatDate(req.completion_date) }}</td>
              <td>{{ req.status }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- My Reviews Tab -->
      <div v-if="activeTab === 'myReviews'" class="tab-pane active">
        <h3>Ratings & Reviews from Customers</h3>
        <table class="table table-hover">
          <thead>
            <tr>
              <th>Request ID</th>
              <th>Customer</th>
              <th>Service</th>
              <th>Rating</th>
              <th>Remarks</th>
              <th>Completed On</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="review in myReviews" :key="review.request_id">
              <td>{{ review.request_id }}</td>
              <td>{{ review.customer_name }}</td>
              <td>{{ review.service_title }}</td>
              <td>{{ review.rating }}</td>
              <td>{{ review.remarks }}</td>
              <td>{{ formatDate(review.completed_on) }}</td>
            </tr>
          </tbody>
        </table>
        <p v-if="!myReviews.length">No reviews found.</p>
      </div>
    </div>
    <div class="how-it-works mt-5 text-center">
      <h4>How It Works</h4>
      <div class="row justify-content-center mt-3">
        <div class="col-md-3">
          <div class="workflow-step p-3">
            <img src="@/assets/illustrations/request.svg" alt="Receive" />
            <p class="mt-2">Receive service requests</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="workflow-step p-3">
            <img src="@/assets/illustrations/accept.svg" alt="Work" />
            <p class="mt-2">Accept and complete them</p>
          </div>
        </div>
        <div class="col-md-3">
          <div class="workflow-step p-3">
            <img src="@/assets/illustrations/money.svg" alt="Pay" />
            <p class="mt-2">Get paid fast</p>
          </div>
        </div>
      </div>
      <p class="quote mt-4 text-muted fst-italic">
        “Your service has the power to change someone’s day.” — ServiGo Team
      </p>
    </div>
  </div>

</template>

<script>
import axios from "axios";

export default {
  name: "ProfessionalDashboard",
  data() {
    return {
      activeTab: "new",
      notification: "",
      notificationType: "info",

      newRequests: [],
      acceptedRequests: [],
      inProgressRequests: [],
      workDoneRequests: [],
      completedRequests: [],
      rejectedRequests: [],

      myReviews: [],
      showEditModal: false,
      editingReview: {},
      editingRating: null,
      editingRemarks: "",
      serviceLookup: {}, // Dictionary mapping service ID to service details
      customerLookup: {}, // Dictionary mapping customer ID to customer details
      professionalId: null,
    };
  },
  watch: {
    activeTab(newVal) {
      if (newVal === "myReviews") {
        this.fetchMyReviews();
      }
    },
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

    async fetchRequests(status, targetArray) {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error(" Missing authorization token.");
          this.showNotification("Please log in to view your requests.", "danger");
          return;
        }

        // Retrieving professionalId either from data or localStorage
        if (!this.professionalId) {
          this.professionalId = localStorage.getItem("professionalId");
        }

        if (!this.professionalId) {
          console.error(" Missing professional ID.");
          this.showNotification("Unable to identify your account. Please log in again.", "danger");
          return;
        }

        // Constructing API URL with the professional's ID and the given status
        let apiURL = `http://localhost:5000/get_requests?professional_id=${this.professionalId}`;
        if (status) {
          apiURL += `&status=${status}`;
        }

        console.log(`🔍 Fetching ${status} requests from API:`, apiURL);

        const response = await fetch(apiURL, {
          method: "GET",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.status === 403) {
          console.error(" Access forbidden: Missing or invalid token.");
          this.showNotification("You are not authorized to view this data.", "danger");
          return;
        }

        const data = await response.json();
        console.log(`✅ API Response (${status} Requests):`, data);

        // Assigning the fetched data to the appropriate array
        this[targetArray] = data;
      } catch (error) {
        console.error(`Error fetching ${status} requests:`, error);
        this.showNotification("An error occurred while fetching requests.", "danger");
      }
    },

    refreshAllRequests() {
      this.fetchRequests("REQUESTED", "newRequests");
      this.fetchRequests("ACCEPTED", "acceptedRequests");
      this.fetchRequests("IN_PROGRESS", "inProgressRequests");
      this.fetchRequests("WORK_DONE", "workDoneRequests");
      this.fetchRequests("COMPLETED", "completedRequests");
      this.fetchRequests("REJECTED", "rejectedRequests");
    },

    async updateRequestStatus(requestId, newStatus, successMessage) {
      try {
        const token = localStorage.getItem("token");
        if (!token) {
          console.error(" Missing authorization token.");
          this.showNotification("Please log in again.", "danger");
          return;
        }

        const response = await fetch(
          "http://localhost:5000/update_request_status",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              request_id: requestId,
              new_status: newStatus,
            }),
          }
        );

        const data = await response.json();
        if (response.ok) {
          console.log(` Request ${requestId} updated to ${newStatus}`);
          this.showNotification(successMessage, "success");
          // Refreshing all request lists after status update
          this.refreshAllRequests();
        } else {
          throw new Error(data.error || "Failed to update request.");
        }
      } catch (error) {
        console.error(` Error updating request ${requestId}:`, error);
        this.showNotification("Server error. Please try again.", "danger");
      }
    },

    acceptRequest(requestId) {
      this.updateRequestStatus(
        requestId,
        "ACCEPTED",
        "Request accepted successfully!"
      );
    },

    rejectRequest(requestId) {
      this.updateRequestStatus(requestId, "REJECTED", "Request rejected.");
    },

    markInProgress(requestId) {
      this.updateRequestStatus(
        requestId,
        "IN_PROGRESS",
        "Work marked as in progress."
      );
    },

    markWorkDone(requestId) {
      this.updateRequestStatus(
        requestId,
        "WORK_DONE",
        "Work marked as done. Awaiting payment."
      );
    },

    finalizeRequest(requestId) {
      this.updateRequestStatus(
        requestId,
        "COMPLETED",
        "Service request finalized!"
      );
    },
    formatDate(isoString) {
      if (!isoString) return "N/A";
      return new Date(isoString).toLocaleString("en-IN", {
        timeZone: "Asia/Kolkata",
      });
    },
    displayStatus(rawStatus) {
      if (rawStatus === "REQUESTED") {
        return "PENDING";
      }
      return rawStatus;
    },
    processPayment(requestId) {
      // Redirecting to Payment page with the request ID as a route parameter
      this.$router.push({ name: "Payment", params: { requestId } });
    },

    fetchMyReviews() {
      const token = localStorage.getItem("token");
      axios
        .get("http://localhost:5000/customer/rating_history", {
          headers: { Authorization: `Bearer ${token}` },
        })
        .then((response) => {
          this.myReviews = response.data;
          console.log("Fetched myReviews:", this.myReviews);
        })
        .catch((err) => {
          console.error("Error fetching reviews:", err);
          alert("Unable to fetch reviews.");
        });
    },

    formatDate(isoString) {
      if (!isoString) return "N/A";
      return new Date(isoString).toLocaleString("en-IN", {
        timeZone: "Asia/Kolkata",
      });
    },
  },

  created() {

    this.professionalId = localStorage.getItem("professionalId");
    if (!this.professionalId) {
      console.error("Professional ID not found in localStorage.");
      this.showNotification("Unable to identify your account. Please log in again.", "danger");
      this.$router.push("/login");
      return;
    }
    // Fetching all request statuses once the component is created
    this.refreshAllRequests();
    this.fetchMyReviews();
  },
};
</script>

<style src="@/assets/css/ProfessionalDashboard.css"></style>
