import apiClient from "../client";
import getImageUrl from "@/helpers/imageUrl";
import { authService } from "./authService";

export const userService = {
  getProfile: async () => {
    const { data } = await apiClient.get("/profile/");
    return data;
  },

  updateProfile: async (formData) => {
    const { data } = await apiClient.patch("/user/", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return data;
  },

  getAvatarUrl: (avatarPath) => getImageUrl(avatarPath),

  formatUsername: (username) => username.replace(/^@/, ""),

  getAvatarInitials: (username) => username.slice(0, 2).toUpperCase(),

  createFormData: (username, file) => {
    const formData = new FormData();
    formData.append("username", username);
    if (file) {
      formData.append("image", file);
    }
    return formData;
  },

  createPreviewUrl: (file) => URL.createObjectURL(file),

  revokePreviewUrl: (previewUrl) => {
    if (previewUrl && !previewUrl.startsWith("http://localhost:8000")) {
      URL.revokeObjectURL(previewUrl);
    }
  },

  getChats: async () => {
    try {
      const response = await apiClient.get("/chats");
      const currentUserId = await authService.getCurrentUserId();

      const chats = response.data.map((chat) => {
        const currentUser = chat.members.find(
          (member) => member.supertokens_id === currentUserId
        );
        const otherMember = chat.members.find(
          (member) => member.supertokens_id !== currentUserId
        );

        return {
          ...chat,
          members: [currentUser, otherMember].filter(Boolean),
        };
      });

      console.log(chats);

      return chats;
    } catch (error) {
      console.error("Error fetching chats:", error);
      throw error;
    }
  },

  deleteChat: async (chatId) => {
    try {
      await apiClient.delete(`/delete_chat/?chat_id=${chatId}`);
    } catch (error) {
      console.error("Error deleting chat:", error);
      throw error;
    }
  },

  sendMessage: async (chatId, message) => {
    try {
      await apiClient.post("/send_message/", {
        chat_id: chatId,
        content: message,
      });
    } catch (error) {
      console.error("Error sending message:", error);
      throw error;
    }
  },

  getMessages: async (chatId) => {
    try {
      const response = await apiClient.get(`/messages/${chatId}`);
      return response.data;
    } catch (error) {
      console.error("Error fetching messages:", error);
      throw error;
    }
  },
};
