import React, {
  createContext,
  useContext,
  useState,
  useCallback,
  useEffect,
} from "react";
import socket from "@/api/socket";

const ChatContext = createContext(null);

export const ChatProvider = ({ children }) => {
  const [selectedChat, setSelectedChat] = useState(null);
  const [onlineUsers, setOnlineUsers] = useState({});

  const selectChat = useCallback((chat) => {
    console.log("Setting selected chat:", chat);
    setSelectedChat(chat);
  }, []);

  useEffect(() => {
    socket.on("online_users", (users) => {
      console.log("Online users updated:", users);
      setOnlineUsers(users);
    });

    socket.emit("get_online_users");

    return () => {
      socket.off("online_users");
    };
  }, []);

  return (
    <ChatContext.Provider
      value={{
        selectedChat,
        setSelectedChat,
        selectChat,
        onlineUsers,
      }}
    >
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
