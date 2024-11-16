import apiClient from "../client";

export const searchService = {
  searchUsers: async (username) => {
    try {
      const response = await apiClient.get(`/search_user`, {
        params: { username },
      });
      return Array.isArray(response.data) ? response.data : [response.data];
    } catch (error) {
      console.error("Search error:", error);
      throw error;
    }
  },

  createChat: async (userId) => {
    try {
      const response = await apiClient.post("/chat_create", userId, {
        withCredentials: true,
      });
      return response.data;
    } catch (error) {
      console.error("Error creating chat:", error);
      throw error;
    }
  },
};
