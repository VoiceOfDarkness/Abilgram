import { useState, useEffect } from "react";
import { userService } from "@/api/services/userService";
import { authService } from "@/api/services/authService";

export const useChatData = (selectedChat) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [currentUserId, setCurrentUserId] = useState(null);

  useEffect(() => {
    const fetchCurrentUserId = async () => {
      try {
        const userId = await authService.getCurrentUserId();
        setCurrentUserId(userId);
      } catch (err) {
        console.error("Error fetching current user ID:", err);
      }
    };

    fetchCurrentUserId();
  }, []);

  useEffect(() => {
    if (selectedChat?.id && currentUserId) {
      setIsLoading(true);
      setError(null);

      try {
        const chatMessages = selectedChat.messages || [];
        const formattedMessages = chatMessages.map((msg) => ({
          ...msg,
          isOwn: msg.sender_id === currentUserId,
        }));

        setMessages(formattedMessages);
      } catch (err) {
        setError("Failed to process chat messages");
        console.error("Error processing chat messages:", err);
      } finally {
        setIsLoading(false);
      }
    } else {
      setMessages([]);
    }
  }, [selectedChat?.id, currentUserId]); // Изменили зависимость на selectedChat?.id

  const addMessage = (newMessage) => {
    if (!newMessage || typeof newMessage !== "object") return;

    setMessages((prev) => [...prev, newMessage]);
  };

  return {
    messages,
    isLoading,
    error,
    currentUserId,
    addMessage,
  };
};
