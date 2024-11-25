import React, { memo, useState, useEffect } from "react";
import ChatList from "./ChatList";
import MessageWindow from "./ChatWindow";
import { useChat } from "@/context/ChatContext";
import useSessionCheck from "../hooks/useSessionCheck";
import { authService } from "@/api/services/authService";
import { userService } from "@/api/services/userService";
import socket from "@/api/socket";

const MemoizedMessageWindow = memo(MessageWindow);

function ChatPage() {
  const { selectedChat, setSelectedChat } = useChat();
  const [chatMessages, setChatMessages] = useState([]);
  const { isLoading } = useSessionCheck();

  const handleSelectChat = async (chat) => {
    setSelectedChat(chat);
    try {
      const messages = await userService.getMessages(chat.id);
      const lastMessage =
        messages.length > 0 ? messages[messages.length - 1] : null;
      console.log("lastMessage", lastMessage);
      setChatMessages(messages);
    } catch (error) {
      console.error("Failed to fetch chat messages:", error);
    }
  };

  const handleDeleteChat = (chatId) => {
    setSelectedChat(null);
    setChatMessages([]);
  };

  return (
    <div className="container mx-auto flex overflow-hidden h-screen">
      <ChatList
        onSelectChat={handleSelectChat}
        onDeleteChat={handleDeleteChat}
      />
      {selectedChat && (
        <MemoizedMessageWindow
          chat={selectedChat}
          messages={chatMessages}
        />
      )}
    </div>
  );
}

export default ChatPage;
