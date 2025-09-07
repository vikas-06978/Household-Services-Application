<template>
  <div class="admin-summary">
    <h1 class="summary-title">Admin Summary</h1>

    <!-- Charts Section -->
    <section class="charts-container">
      <!-- Service Requests by Status -->
      <div class="chart-card">
        <h2>Service Requests by Status</h2>
        <canvas ref="serviceRequestsChartRef" id="serviceRequestsChart"></canvas>
      </div>

      <!-- Professional Ratings Distribution -->
      <div class="chart-card">
        <h2>Professional Ratings Distribution</h2>
        <canvas ref="professionalRatingsChartRef" id="professionalRatingsChart"></canvas>
      </div>

      <!-- User Stats (Active/Blocked) -->
      <div class="chart-card">
        <h2>User Stats</h2>
        <canvas ref="userStatsChartRef" id="userStatsChart"></canvas>
      </div>

      <!--  Services Overview -->
      <div class="chart-card">
        <h2>Services Overview</h2>
        <canvas ref="servicesChartRef" id="servicesChart"></canvas>
      </div>
    </section>
  </div>
</template>

<script>
import axios from "axios";
import Chart from "chart.js/auto";

export default {
  data() {
    return {
      serviceRequestsData: null,
      professionalRatingsData: null,
      userStatsData: null,
      servicesOverviewData: null,
      serviceRequestsChart: null,
      professionalRatingsChart: null,
      userStatsChart: null,
      servicesChart: null,
    };
  },
  mounted() {
    this.fetchAllData();
    const debouncedThemeUpdate = this.debounce(() => {
      this.updateAllCharts();
    }, 150);
    const observer = new MutationObserver(() => {
      debouncedThemeUpdate();
    });

    observer.observe(document.documentElement, {
      attributes: true,
      attributeFilter: ["data-theme"],
    });
  },
  methods: {
    // Detecting current theme (light/dark)
    getThemeMode() {
      return document.documentElement.getAttribute("data-theme") || "light";
    },

    getThemeColors() {
      const isDark = this.getThemeMode() === "dark";
      return {
        textColor: isDark ? "#f1f1f1" : "#2c3e50",
        gridColor: isDark ? "#444" : "#ccc",
      };
    },

    // Fetching All Charts Data
    fetchAllData() {
      axios
        .get("/api/admin/service_requests_by_status")
        .then((res) => {
          this.serviceRequestsData = res.data;
          this.$nextTick(() => this.renderServiceRequestsChart());
        })
        .catch(() => {
          this.serviceRequestsData = {
            labels: [
              "Pending",
              "Accepted",
              "In Progress",
              "Work Done",
              "Rejected",
              "Completed",
            ],
            data: [10, 4, 5, 2, 3, 8],
          };
          this.$nextTick(() => this.renderServiceRequestsChart());
        });

      axios
        .get("/api/admin/professional_ratings_distribution")
        .then((res) => {
          this.professionalRatingsData = res.data;
          this.$nextTick(() => this.renderProfessionalRatingsChart());
        })
        .catch(() => {
          this.professionalRatingsData = {
            labels: ["1-2", "2-3", "3-4", "4-5"],
            data: [2, 5, 10, 8],
          };
          this.$nextTick(() => this.renderProfessionalRatingsChart());
        });

      axios
        .get("/api/admin/user_stats")
        .then((res) => {
          this.userStatsData = res.data;
          this.$nextTick(() => this.renderUserStatsChart());
        })
        .catch(() => {
          this.userStatsData = {
            labels: [
              "Active Customers",
              "Blocked Customers",
              "Active Pros",
              "Blocked Pros",
            ],
            data: [50, 5, 20, 2],
          };
          this.$nextTick(() => this.renderUserStatsChart());
        });

      axios
        .get("/api/admin/services_overview")
        .then((res) => {
          this.servicesOverviewData = res.data;
          this.$nextTick(() => this.renderServicesChart());
        })
        .catch(() => {
          this.servicesOverviewData = {
            labels: ["Plumbing", "Cleaning", "Electrician", "Carpentry"],
            data: [30, 50, 25, 10],
          };
          this.$nextTick(() => this.renderServicesChart());
        });
    },

    // Service Requests by Status
    renderServiceRequestsChart() {
      const { labels, data } = this.serviceRequestsData;
      const { textColor, gridColor } = this.getThemeColors();

      const canvas = this.$refs.serviceRequestsChartRef;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      if (this.serviceRequestsChart) this.serviceRequestsChart.destroy();
      this.serviceRequestsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Requests",
              data,
              backgroundColor: [
                "#FFA726",
                "#42A5F5",
                "#66BB6A",
                "#FB8C00",
                "#EF5350",
                "#AB47BC",
              ],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              ticks: {
                color: textColor,
                stepSize: 1,
                callback: function (value) {
                  return Number.isInteger(value) ? value : '';
                },
              },
              grid: { color: gridColor },
            },
            x: {
              ticks: { color: textColor },
              grid: { display: false },
            },
          }
        },
      });
    },

    // Professional Ratings Distribution
    renderProfessionalRatingsChart() {
      const { labels, data } = this.professionalRatingsData;
      const { textColor, gridColor } = this.getThemeColors();
      const canvas = this.$refs.professionalRatingsChartRef;
      if (!canvas) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      if (this.professionalRatingsChart)
        this.professionalRatingsChart.destroy();
      this.professionalRatingsChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Ratings",
              data,
              backgroundColor: "#8E44AD",
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, color: textColor },
              grid: { color: gridColor },
            },
            x: {
              ticks: { color: textColor },
              grid: { color: gridColor },
            },
          },
        },
      });
    },

    // User Stats (Doughnut)
    renderUserStatsChart() {
      const { labels, data } = this.userStatsData;
      const { textColor } = this.getThemeColors();
      const canvas = this.$refs.userStatsChartRef;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;
      if (this.userStatsChart) this.userStatsChart.destroy();
      this.userStatsChart = new Chart(ctx, {
        type: "doughnut",
        data: {
          labels,
          datasets: [
            {
              data,
              backgroundColor: ["#2ECC71", "#E74C3C", "#3498DB", "#F1C40F"],
            },
          ],
        },
        options: {
          responsive: true,
          plugins: {
            legend: {
              labels: { color: textColor },
            },
          },
        },
      });
    },

    // Services Overview
    renderServicesChart() {
      const { labels, data } = this.servicesOverviewData;
      const { textColor, gridColor } = this.getThemeColors();

      const canvas = this.$refs.servicesChartRef;
      if (!canvas) return;
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      if (this.servicesChart) this.servicesChart.destroy();
      this.servicesChart = new Chart(ctx, {
        type: "bar",
        data: {
          labels,
          datasets: [
            {
              label: "Usage",
              data,
              backgroundColor: ["#1ABC9C", "#F39C12", "#9B59B6", "#E67E22"],
              borderWidth: 1,
            },
          ],
        },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: {
            y: {
              beginAtZero: true,
              ticks: { stepSize: 1, color: textColor },
              grid: { color: gridColor },
            },
            x: {
              ticks: { color: textColor },
              grid: { color: gridColor },
            },
          },
        },
      });
    },
    updateAllCharts() {
      // Destroying all charts safely first
      if (this.serviceRequestsChart) {
        this.serviceRequestsChart.destroy();
        this.serviceRequestsChart = null;
      }
      if (this.professionalRatingsChart) {
        this.professionalRatingsChart.destroy();
        this.professionalRatingsChart = null;
      }
      if (this.userStatsChart) {
        this.userStatsChart.destroy();
        this.userStatsChart = null;
      }
      if (this.servicesChart) {
        this.servicesChart.destroy();
        this.servicesChart = null;
      }

      // Waiting for DOM to repaint theme changes
      setTimeout(() => {
        this.$nextTick(() => {
          if (this.serviceRequestsData && this.$refs.serviceRequestsChartRef) {
            this.renderServiceRequestsChart();
          }
          if (
            this.professionalRatingsData &&
            this.$refs.professionalRatingsChartRef
          ) {
            this.renderProfessionalRatingsChart();
          }
          if (this.userStatsData && this.$refs.userStatsChartRef) {
            this.renderUserStatsChart();
          }
          if (this.servicesOverviewData && this.$refs.servicesChartRef) {
            this.renderServicesChart();
          }
        });
      }, 150);
    },
    debounce(fn, wait = 100) {
      let timeout;
      return (...args) => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
          fn.apply(this, args);
        }, wait);
      };
    }
  },
};
</script>

<style src="@/assets/css/AdminSummary.css"></style>
