import axios from "axios";

const API_BASE_URL = `${import.meta.env.VITE_API_URL || ""}/api/v1`;

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export default apiClient;
