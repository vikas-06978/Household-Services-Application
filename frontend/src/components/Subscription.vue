<template>
  <div class="subscription-container">
    <!-- Main Heading -->
    <h2 class="text-center mb-4 subscription-title"> Subscription Overview</h2>

    <!-- Feedback Message -->
    <div v-if="statusMessage" :class="'alert alert-' + statusCategory">
      {{ statusMessage }}
    </div>

    <!-- Subscription Status Card -->
    <div class="card p-4 text-center manage-plan-card">
      <template v-if="subscriptionStatus === 'active' && hasPaid">
        <h4 class="text-success mb-2 plan-status-box">You're a Premium Member!</h4>
        <p>
          Your subscription is active until:
          <strong>{{ subscriptionExpiry || expiryDateDisplay }}</strong>
        </p>
      </template>

      <template v-else-if="subscriptionStatus === 'inactive' && hasPaid">
        <h4 class="text-warning mb-2">Subscription Inactive</h4>
        <p>⚠️ You have cancelled your premium membership.</p>
      </template>

      <template v-else>
        <h4 class="text-danger mb-2 btn btn-danger cancel-btn">No Active Subscription</h4>
        <p> You are not subscribed to premium currently.</p>
      </template>
    </div>

    <!-- Action Buttons -->
    <div class="text-center mt-3">
      <!-- Show only if user has paid -->
      <template v-if="hasPaid">
        <button v-if="subscriptionStatus === 'active'" class="btn btn-outline-danger" @click="cancelSubscription">
          Cancel Premium Subscription
        </button>

        <button v-else-if="subscriptionStatus === 'inactive'" class="btn btn-outline-success"
          @click="activateSubscription">
          Reactivate Premium Subscription
        </button>
      </template>

      <!-- If never paid, show Subscribe Now -->
      <button v-else class="btn btn-primary" @click="subscribeUser">
        💎 Subscribe Now for ₹{{ subscriptionFee }}
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "Subscription",
  data() {
    return {
      subscriptionStatus: "none", // active | inactive | none
      subscriptionExpiry: null,
      subscriptionFee: 20.0,
      statusMessage: "",
      statusCategory: "",
      hasPaid: false,
    };
  },
  computed: {
    expiryDateDisplay() {
      return this.subscriptionExpiry
        ? new Date(this.subscriptionExpiry).toLocaleString()
        : "N/A";
    },
  },
  methods: {
    async fetchSubscriptionStatus() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.statusMessage = "Please log in.";
        this.statusCategory = "danger";
        return;
      }
      try {
        const response = await fetch(
          "http://localhost:5000/api/customer/subscription_status",
          {
            method: "GET",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (!response.ok) {
          this.statusMessage = "Error fetching subscription status.";
          this.statusCategory = "danger";
          return;
        }

        const data = await response.json();

        this.subscriptionStatus = data.subscription_status || "none";
        this.subscriptionExpiry = data.subscription_expiry || null;
        this.hasPaid = data.has_paid || false; // NEW
      } catch (error) {
        console.error("Error in fetchSubscriptionStatus:", error);
        this.statusMessage = "An error occurred.";
        this.statusCategory = "danger";
      }
    },

    async subscribeUser() {
      const token = localStorage.getItem("token");
      if (!token) {
        this.statusMessage = "Please log in.";
        this.statusCategory = "danger";
        return;
      }
      try {
        const response = await fetch(
          "http://localhost:5000/api/customer/subscribe",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({ amount: this.subscriptionFee }),
          }
        );

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Subscription failed");

        this.statusMessage = data.message;
        this.statusCategory = "success";
        await this.fetchSubscriptionStatus();
      } catch (error) {
        this.statusMessage = error.message;
        this.statusCategory = "danger";
      }
    },

    async cancelSubscription() {
      const confirmCancel = confirm("Cancel your subscription?");
      if (!confirmCancel) return;

      const token = localStorage.getItem("token");
      try {
        const response = await fetch(
          "http://localhost:5000/api/customer/cancel_subscription",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Failed");

        this.statusMessage = data.message;
        this.statusCategory = "success";
        await this.fetchSubscriptionStatus();
      } catch (error) {
        this.statusMessage = error.message;
        this.statusCategory = "danger";
      }
    },

    async activateSubscription() {
      const token = localStorage.getItem("token");
      try {
        const response = await fetch(
          "http://localhost:5000/api/customer/activate_subscription",
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const data = await response.json();
        if (!response.ok) throw new Error(data.error || "Activation failed");

        this.statusMessage = data.message;
        this.statusCategory = "success";
        await this.fetchSubscriptionStatus();
      } catch (error) {
        this.statusMessage = error.message;
        this.statusCategory = "danger";
      }
    },
  },
  mounted() {
    this.fetchSubscriptionStatus();
  },
};
</script>

<style src="@/assets/css/Subscription.css"></style>
