import { createRouter, createWebHistory } from "vue-router";
import Login from "./components/Login.vue";
import Signup from "./components/Signup.vue";
import AdminDashboard from "./components/AdminDashboard.vue";
import CustomerDashboard from "./components/CustomerDashboard.vue";
import ProfessionalDashboard from "./components/ProfessionalDashboard.vue";
import CustomerSummary from "./components/CustomerSummary.vue";
import ProfessionalSummary from "./components/ProfessionalSummary.vue";
import AdminSummary from "./components/AdminSummary.vue";
import CustomerSearch from "./components/CustomerSearch.vue";
import ProfessionalSearch from "./components/ProfessionalSearch.vue";
import AdminSearch from "./components/AdminSearch.vue";
import Profile from "./components/Profile.vue";
import Payment from "./components/Payment.vue";
import Subscription from "./components/Subscription.vue";

const routes = [
  { path: "/", redirect: "/login" },
  { path: "/login", name: "login", component: Login },
  { path: "/signup", name: "signup", component: Signup },
  {
    path: "/profile",
    name: "profile",
    component: Profile,
    meta: { requiresAuth: true },
  },

  // Role-based Dashboard Routes only get into the dashboard which he belongs to
  {
    path: "/admin/dashboard",
    name: "adminDashboard",
    component: AdminDashboard,
    meta: { requiresAuth: true, role: "ADMIN" },
  },
  {
    path: "/customer/dashboard",
    name: "customerDashboard",
    component: CustomerDashboard,
    meta: { requiresAuth: true, role: "CUSTOMER" },
  },
  {
    path: "/professional/dashboard",
    name: "professionalDashboard",
    component: ProfessionalDashboard,
    meta: { requiresAuth: true, role: "PROFESSIONAL" },
  },

  // Role-based Summary Routes for each user & admin
  {
    path: "/admin/summary",
    name: "adminSummary",
    component: AdminSummary,
    meta: { requiresAuth: true, role: "ADMIN" },
  },
  {
    path: "/customer/summary",
    name: "customerSummary",
    component: CustomerSummary,
    meta: { requiresAuth: true, role: "CUSTOMER" },
  },
  {
    path: "/professional/summary",
    name: "professionalSummary",
    component: ProfessionalSummary,
    meta: { requiresAuth: true, role: "PROFESSIONAL" },
  },

  // Role-based Search Routes for admin, customers & professionals
  {
    path: "/admin/search",
    name: "adminSearch",
    component: AdminSearch,
    meta: { requiresAuth: true, role: "ADMIN" },
  },
  {
    path: "/customer/search",
    name: "customerSearch",
    component: CustomerSearch,
    meta: { requiresAuth: true, role: "CUSTOMER" },
  },
  {
    path: "/professional/search",
    name: "professionalSearch",
    component: ProfessionalSearch,
    meta: { requiresAuth: true, role: "PROFESSIONAL" },
  },

  // Payment route
  { path: "/payment/:requestId", name: "Payment", component: Payment },

  {
    path: "/subscription",
    name: "Subscription",
    component: Subscription,
    meta: { requiresAuth: true },
  },

  {
    path: "/admin/summary",
    name: "AdminSummary",
    component: AdminSummary,
    meta: { requiresAuth: true, role: "ADMIN" },
  },

  {
    path: "/create-service",
    name: "CreateService",
    component: () => import("@/components/CreateService.vue"),
    meta: { hideNavbar: true },
  },
  {
    path: "/admin-dashboard",
    name: "AdminDashboard",
    component: () => import("@/components/AdminDashboard.vue"),
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Navigation Guard - Role-Based Access Control accross application
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem("token");
  const userRole = localStorage.getItem("role");

  //  If the route requires authentication and there's no token, redirect back it to login page
  if (to.meta.requiresAuth && !token) {
    console.warn(" Unauthorized Access! Redirecting to login...");
    return next("/login");
  }

  //  Redirecting users to their correct dashboard if they try accessing another role's page
  if (to.meta.requiresAuth && to.meta.role && to.meta.role !== userRole) {
    console.warn(
      " Unauthorized Role Access! Redirecting to the correct dashboard..."
    );
    if (userRole === "ADMIN") return next("/admin/dashboard");
    if (userRole === "CUSTOMER") return next("/customer/dashboard");
    if (userRole === "PROFESSIONAL") return next("/professional/dashboard");
    return next("/login");
  }

  next();
});

export default router;
