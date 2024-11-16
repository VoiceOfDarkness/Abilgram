import React, { useState, useEffect } from "react";
import { ScrollArea } from "./ui/scroll-area";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import ListSearch from "./Search";
import getImageUrl from "@/helpers/imageUrl";
import { userService } from "@/api/services/userService";
import { authService } from "@/api/services/authService";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import socket from "@/api/socket";

function ChatList({ onSelectChat, onDeleteChat }) {
  const [currentUserId, setCurrentUserId] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [chats, setChats] = useState([]);
  const [error, setError] = useState(null);
  const [deletingChat, setDeletingChat] = useState(null);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);

  useEffect(() => {
    const fetchInitialData = async () => {
      try {
        const [userId, chatsData] = await Promise.all([
          authService.getCurrentUserId(),
          userService.getChats(),
        ]);
        setCurrentUserId(userId);
        setChats(chatsData);
        console.log("Chats data:", chatsData);
      } catch (error) {
        console.error("Error fetching initial data:", error);
        setError("Failed to fetch initial data. Please try again.");
      }
    };

    fetchInitialData();
  }, []);

  useEffect(() => {
    const handleNewChat = (newChat) => {
      console.log("New chat received:", newChat);
      setChats((prevChats) => [...prevChats, newChat]);
    };

    socket.on("new_chat", handleNewChat);

    return () => {
      socket.off("new_chat", handleNewChat);
    };
  }, []);

  const fetchChats = async () => {
    try {
      const chatsData = await userService.getChats();
      setChats(chatsData);
    } catch (error) {
      console.error("Error fetching chats:", error);
      setError("Failed to fetch chats. Please try again.");
    }
  };

  const handleDeleteChat = async (chatId) => {
    try {
      await userService.deleteChat(chatId);
      setChats(chats.filter((chat) => chat.id !== chatId));
      setDeletingChat(null);
      setIsDropdownOpen(false);
      onDeleteChat(chatId);
    } catch (error) {
      console.error("Error deleting chat:", error);
    }
  };

  const handleContextMenu = (e, chat) => {
    e.preventDefault();
    setDeletingChat(chat);
    setIsDropdownOpen(true);
  };

  return (
    <div className="relative flex flex-col w-1/4 bg-gray-800">
      <ListSearch
        searchQuery={searchQuery}
        setSearchQuery={setSearchQuery}
        onChatCreate={fetchChats}
      />
      <h2 className="text-lg font-bold mb-2 p-4">Chats</h2>
      <ScrollArea className="flex flex-col h-full p-3 space-y-2">
        {chats.map((chat) => (
          <div
            key={chat.id}
            onContextMenu={(e) => handleContextMenu(e, chat)}
            onClick={() => onSelectChat(chat)}
            className="p-3 bg-gray-800 rounded-md flex items-center gap-2 cursor-pointer hover:bg-gray-700 relative"
          >
            <Avatar className="w-10 h-10 border border-gray-600">
              <AvatarImage
                src={getImageUrl(chat.members[1].avatar_url)}
                alt={chat.name}
              />
              <AvatarFallback className="bg-cyan-950">
                {chat.members[1].username?.slice(0, 2).toUpperCase()}
              </AvatarFallback>
            </Avatar>
            <div>
              <p className="text-white">{chat.members[1].username}</p>
              <p className="text-gray-400 text-sm truncate">
                {chat.lastMessage || ""}
              </p>
            </div>

            <DropdownMenu
              open={isDropdownOpen && deletingChat?.id === chat.id}
              onOpenChange={setIsDropdownOpen}
            >
              <DropdownMenuTrigger>
                <div className="p-2 hover:bg-gray-700 rounded-md absolute top-2 right-2"></div>
              </DropdownMenuTrigger>
              <DropdownMenuContent className="absolute top-0 left-20">
                <DropdownMenuItem
                  onClick={() => handleDeleteChat(chat.id)}
                  className="text-red-600 hover:bg-red-100 hover:text-red-700 transition-colors duration-200 ease-in-out"
                >
                  Delete Chat
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        ))}
      </ScrollArea>
    </div>
  );
}

export default ChatList;
