<template>
  <div class="professional-summary">
    <h1 class="summary-title">Professional Summary</h1>

    <!-- Charts Section -->
    <section class="charts-container">
      <!-- My Requests by Status -->
      <div class="chart-card">
        <h2>My Requests by Status</h2>
        <canvas id="requestsStatusChart"></canvas>
      </div>

      <!-- Services Overview -->
      <div class="chart-card">
        <h2>Services Overview</h2>
        <canvas id="servicesOverviewChart"></canvas>
      </div>
    </section>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  name: "ProfessionalSummary",
  data() {
    return {
      // Data for the two charts
      requestsStatusData: null,
      servicesOverviewData: null,

      professionalId: null,
      statusChartInstance: null,
      servicesChartInstance: null
    };
  },
  mounted() {
    const themeObserver = new MutationObserver(() => {
      if (this.requestsStatusData) this.renderRequestsStatusChart();
      if (this.servicesOverviewData) this.renderServicesOverviewChart();
    });
    themeObserver.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ['data-theme']
    });

    const storedId = localStorage.getItem("professionalId");
    if (!storedId) {
      console.warn(
        "No professional ID found in localStorage. Please set it or retrieve it from route/JWT."
      );
      return;
    }
    this.professionalId = storedId;

    // Fetching data for both charts using the dynamic professionalId
    this.fetchRequestsByStatus();
    this.fetchServicesOverview();
  },
  computed: {
  },
  methods: {
    // Fetching & Rendering Requests by Status
    fetchRequestsByStatus() {
      axios
        .get(
          `/api/professional/requests_by_status?professional_id=${this.professionalId}`
        )
        .then((response) => {
          this.requestsStatusData = response.data;
          this.renderRequestsStatusChart();
        })
        .catch((error) => {
          console.error("Error fetching requests by status:", error);
          this.requestsStatusData = {
            labels: ["Pending", "In Progress", "Completed", "Rejected"],
            data: [2, 4, 8, 1],
          };
          this.renderRequestsStatusChart();
        });
    },
    renderRequestsStatusChart() {
      if (!this.requestsStatusData) return;

      this.$nextTick(() => {
        const canvas = document.getElementById("requestsStatusChart");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Destroying previous chart if exists
        if (this.statusChartInstance) {
          this.statusChartInstance.destroy();
        }

        const textColor = getComputedStyle(document.documentElement)
          .getPropertyValue('--text-color')
          .trim();

        this.statusChartInstance = new Chart(ctx, {
          type: "bar",
          data: {
            labels: this.requestsStatusData.labels,
            datasets: [{
              label: "Requests",
              data: this.requestsStatusData.data,
              backgroundColor: ["#FFA726", "#42A5F5", "#66BB6A", "#EF5350", "#AB47BC"]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false }
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  color: textColor,
                  stepSize: 1,
                  callback: function (value) {
                    return Number.isInteger(value) ? value : '';
                  }
                },
                grid: { color: "rgba(255,255,255,0.1)" }
              },
              x: {
                ticks: { color: textColor },
                grid: { color: "rgba(255,255,255,0.05)" }
              }
            }
          }
        });
      });
    },

    // Fetching & Rendering Services Overview
    fetchServicesOverview() {
      axios
        .get(
          `/api/professional/services_overview?professional_id=${this.professionalId}`
        )
        .then((response) => {
          this.servicesOverviewData = response.data;
          this.renderServicesOverviewChart();
        })
        .catch((error) => {
          console.error("Error fetching services overview:", error);

          this.servicesOverviewData = {
            labels: ["Haircut", "Painting", "Facial", "Plumbing"],
            data: [5, 3, 2, 1],
          };
          this.renderServicesOverviewChart();
        });
    },
    renderServicesOverviewChart() {
      if (!this.servicesOverviewData) return;

      this.$nextTick(() => {
        const canvas = document.getElementById("servicesOverviewChart");
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Destroying previous chart
        if (this.servicesChartInstance) {
          this.servicesChartInstance.destroy();
        }

        const textColor = getComputedStyle(document.documentElement)
          .getPropertyValue('--text-color')
          .trim();

        this.servicesChartInstance = new Chart(ctx, {
          type: "pie",
          data: {
            labels: this.servicesOverviewData.labels,
            datasets: [{
              label: "Services",
              data: this.servicesOverviewData.data,
              backgroundColor: ["#FF7043", "#42A5F5", "#66BB6A", "#FFCA28", "#EC407A"]
            }]
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: {
                  color: textColor,
                  font: { size: 14 }
                }
              }
            }
          }
        });
      });
    }
  },
};

</script>

<style src="@/assets/css/ProfessionalSummary.css"></style>
