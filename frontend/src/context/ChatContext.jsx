import React, { createContext, useContext, useState, useCallback } from "react";

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [selectedChat, setSelectedChat] = useState(null);

  const selectChat = useCallback((chat) => {
    console.log("Setting selected chat:", chat);
    setSelectedChat(chat);
  }, []);

  return (
    <ChatContext.Provider value={{ selectedChat, setSelectedChat, selectChat }}>
      {children}
    </ChatContext.Provider>
  );
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error("useChat must be used within a ChatProvider");
  }
  return context;
};
