<template>
  <div class="customer-summary">
    <h1 class="summary-title">Customer Summary</h1>

    <!-- Charts Section -->
    <section class="charts-container">
      <!-- Service Requests by Status -->
      <div class="chart-card">
        <h2>Service Requests by Status</h2>
        <canvas id="serviceRequestsChart" ref="serviceRequestsChartRef"></canvas>
      </div>

      <!--  Services Overview -->
      <div class="chart-card">
        <h2>Services Overview</h2>
        <canvas id="servicesChart" ref="servicesChartRef"></canvas>
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
      servicesData: null,
      serviceChart: null,
      servicesChart: null,
    };
  },
  mounted() {
    this.fetchServiceRequestsStats();
    this.fetchServicesOverview();
    this.setupThemeListener();
  },
  methods: {
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

    setupThemeListener() {
      const observer = new MutationObserver(() => {
        if (this.serviceRequestsData) this.renderServiceRequestsChart();
        if (this.servicesData) this.renderServicesChart();
      });

      observer.observe(document.documentElement, {
        attributes: true,
        attributeFilter: ["data-theme"],
      });
    },

    fetchServiceRequestsStats() {
      axios
        .get("/api/customer/service_requests_stats")
        .then((res) => {
          this.serviceRequestsData = res.data;
          this.renderServiceRequestsChart();
        })
        .catch(() => {
          this.serviceRequestsData = {
            labels: ["Pending", "Accepted", "In Progress", "Work Done", "Rejected", "Completed"],
            data: [3, 2, 5, 1, 2, 4]
          };
          this.renderServiceRequestsChart();
        });
    },

    renderServiceRequestsChart() {
      this.$nextTick(() => {
        const canvas = this.$refs.serviceRequestsChartRef;
        if (!canvas) return;

        if (this.serviceChart) {
          this.serviceChart.destroy();
          this.serviceChart = null;
        }

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const { textColor, gridColor } = this.getThemeColors();
        const { labels, data } = this.serviceRequestsData;

        this.serviceChart = new Chart(ctx, {
          type: "bar",
          data: {
            labels,
            datasets: [
              {
                label: "Requests",
                data,
                backgroundColor: ["#FFA726", "#42A5F5", "#66BB6A", "#FB8C00", "#EF5350", "#AB47BC"],
              },
            ],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: { display: false },
            },
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
      });
    },

    fetchServicesOverview() {
      axios
        .get("/api/customer/services_overview")
        .then((res) => {
          this.servicesData = res.data;
          this.renderServicesChart();
        })
        .catch(() => {
          this.servicesData = {
            labels: ["Haircut", "Massage", "Facial", "Manicure", "Pedicure"],
            data: [3, 2, 1, 4, 2],
          };
          this.renderServicesChart();
        });
    },

    renderServicesChart() {
      this.$nextTick(() => {
        const canvas = this.$refs.servicesChartRef;
        if (!canvas) return;

        if (this.servicesChart) {
          this.servicesChart.destroy();
          this.servicesChart = null;
        }

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const { textColor } = this.getThemeColors();
        const { labels, data } = this.servicesData;
        const colors = ["#FF7043", "#42A5F5", "#66BB6A", "#FFCA28", "#EC407A"];

        this.servicesChart = new Chart(ctx, {
          type: "pie",
          data: {
            labels,
            datasets: [{ label: "Services", data, backgroundColor: colors }],
          },
          options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: {
                  color: textColor,
                  font: { size: 14 },
                },
              },
            },
          },
        });
      });
    },
  },
};

</script>

<style src="@/assets/css/CustomerSummary.css"></style>
