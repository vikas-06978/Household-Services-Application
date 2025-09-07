<template>
  <div class="container payment-container">
    <h2>Make Payment</h2>
    <div v-if="message" :class="'alert alert-' + category">{{ message }}</div>

    <!-- Payment Form -->
    <form @submit.prevent="processPayment" v-if="!paymentDone">
      <!-- Card Number Input -->
      <div class="form-group">
        <label>Card Number:</label>
        <input type="text" v-model="cardNumber" required class="form-control" @input="formatCardNumber"
          placeholder="1111-1111-1111-1111" />
      </div>

      <!-- Expiry Date Input -->
      <div class="form-group">
        <label>Expiry Date (MM/YY):</label>
        <input type="text" v-model="expiryDate" required class="form-control" @input="formatExpiryDate"
          placeholder="MM/YY" />
      </div>

      <!-- CVV Input -->
      <div class="form-group">
        <label>CVV:</label>
        <input type="text" v-model="cvv" required class="form-control" pattern="^[0-9]{3}$"
          title="Enter a valid 3-digit CVV" placeholder="123" />
      </div>

      <button type="submit" class="btn btn-success">Pay Now</button>
    </form>

    <!-- Rating Form  -->
    <div v-if="paymentDone && !ratingDone">
      <h3>Rate Your Professional</h3>
      <div class="form-group">
        <label>Rating (1-5):</label>
        <input type="number" v-model="rating" min="1" max="5" class="form-control" required />
      </div>
      <div class="form-group">
        <label>Remarks:</label>
        <textarea v-model="remarks" placeholder="Leave a review..." class="form-control"></textarea>
      </div>
      <button @click="submitRating" class="btn btn-primary">
        Submit Rating
      </button>
    </div>

    <!-- Mark as Completed Button -->
    <div v-if="ratingDone">
      <button @click="markAsCompleted" class="btn btn-success">
        Mark as Completed
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: "Payment",
  data() {
    return {
      message: null,
      category: null,
      cardNumber: "",
      expiryDate: "",
      cvv: "",
      rating: null,
      remarks: "",
      paymentDone: false,
      ratingDone: false,
      requestId: null,
      authenticated: !!localStorage.getItem("token"),
      isLoading: false,
    };
  },
  computed: {
    computedRequestId() {
      return this.$route.params.requestId || null;
    },
  },
  mounted() {
    this.requestId = this.$route.params.requestId || null;
  },
  methods: {
    formatCardNumber() {
      // Removing all non-digit characters
      let digits = this.cardNumber.replace(/\D/g, "");
      // Limiting to 16 digits maximum
      digits = digits.substring(0, 16);
      // Auto-inserting hyphens every 4 digits
      const groups = digits.match(/.{1,4}/g) || [];
      this.cardNumber = groups.join("-");
    },
    formatExpiryDate() {
      // Removing non-digit characters
      let digits = this.expiryDate.replace(/\D/g, "");
      // Limiting to 4 digits (MMYY)
      digits = digits.substring(0, 4);
      // Auto-inserting slash after 2 digits if applicable
      if (digits.length >= 3) {
        this.expiryDate = digits.substring(0, 2) + "/" + digits.substring(2);
      } else {
        this.expiryDate = digits;
      }
    },
    async fetchWithAuth(url, options = {}) {
      const token = localStorage.getItem("token");
      if (!token) {
        this.message = "Authentication required. Please log in.";
        this.category = "danger";
        this.$router.push("/login");
        return null;
      }
      const headers = {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
      };
      try {
        const response = await fetch(url, { ...options, headers });
        const data = await response.json();
        if (!response.ok) {
          if (response.status === 401) {
            this.message = "Session expired. Please log in again.";
            this.category = "danger";
            localStorage.removeItem("token");
            this.$router.push("/login");
          }
          return null;
        }
        return { response, data };
      } catch (error) {
        console.error(` Error fetching ${url}:`, error);
        this.message = "An error occurred. Please try again.";
        this.category = "danger";
        return null;
      }
    },
    async processPayment() {
      const rawDigits = this.cardNumber.replace(/-/g, "");
      if (rawDigits.length !== 16) {
        this.message = "Please enter a valid 16-digit card number.";
        this.category = "danger";
        return;
      }
      const [mm, yy] = this.expiryDate.split("/");
      if (!mm || !yy || mm.length !== 2 || yy.length !== 2) {
        this.message = "Please enter a valid expiry date in MM/YY format.";
        this.category = "danger";
        return;
      }
      if (!/^\d{3}$/.test(this.cvv)) {
        this.message = "Please enter a valid 3-digit CVV.";
        this.category = "danger";
        return;
      }
      const result = await this.fetchWithAuth(
        `http://localhost:5000/customer/payment/${this.requestId}`,
        {
          method: "POST",
        }
      );
      if (result) {
        this.message = result.data.message;
        this.category = result.data.category;
        if (result.response.ok) {
          this.paymentDone = true; // Payment Successful
        }
      }
    },
    async submitRating() {
      if (!this.requestId) {
        this.message = "Invalid request. Please try again.";
        this.category = "danger";
        return;
      }
      const result = await this.fetchWithAuth(
        `http://localhost:5000/customer/rate/${this.requestId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            rating: this.rating,
            remarks: this.remarks,
          }),
        }
      );
      if (result) {
        this.message = result.data.message;
        this.category = result.data.category;
        if (result.response.ok) {
          this.ratingDone = true; // Rating Submitted
        }
      }
    },
    async markAsCompleted() {
      if (this.isLoading || !this.requestId) return;
      this.isLoading = true;

      const result = await this.fetchWithAuth(
        `http://localhost:5000/customer/complete/${this.requestId}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({}),
        }
      );
      if (!result) {
        this.isLoading = false;
        return;
      }
      if (result.response.ok) {
        this.message = result.data.message;
        this.category = result.data.category;
        try {
          const dashboardResult = await this.fetchWithAuth(
            "http://localhost:5000/api/customer/dashboard",
            {
              method: "GET",
            }
          );
          if (dashboardResult && dashboardResult.response.ok) {
            this.$router.push("/customer/dashboard");
          } else {
            throw new Error("Unauthorized access!");
          }
        } catch (error) {
          console.error("Error fetching dashboard:", error);
          this.message = "Session expired. Please log in again.";
          this.category = "danger";
          localStorage.removeItem("token");
          this.$router.push("/login");
        }
      }
      this.isLoading = false;
    },
  },
};
</script>

<style src="@/assets/css/Payment.css"></style>
