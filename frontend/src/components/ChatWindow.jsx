import { useState, useEffect, useRef } from "react";
import { IoSend } from "react-icons/io5";
import getImageUrl from "@/helpers/imageUrl";
import { userService } from "@/api/services/userService";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { authService } from "@/api/services/authService";
import { useChat } from "@/context/ChatContext";
import socket from "@/api/socket";

function MessageHeader() {
  const { selectedChat } = useChat();

  return selectedChat ? (
    <div className="flex items-center justify-between p-4 bg-gray-800 relative z-10 sticky top-0">
      <div className="flex items-center">
        <Avatar className="w-10 h-10 rounded-full">
          <AvatarImage
            src={getImageUrl(selectedChat.members[1].avatar_url)}
            alt={selectedChat.name}
          />
          <AvatarFallback className="bg-cyan-950">
            {selectedChat.members[1].username?.slice(0, 2).toUpperCase()}
          </AvatarFallback>
        </Avatar>
        <div className="ml-4">
          <p className="font-bold">{selectedChat.members[1].username}</p>
          <p className="text-gray-400">Active now</p>
        </div>
      </div>
    </div>
  ) : null;
}

function MessageWindow() {
  const { selectedChat } = useChat();
  const [messages, setMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const [currentUserId, setCurrentUserId] = useState(null);

  // Get current user on component mount
  useEffect(() => {
    const fetchCurrentUserId = async () => {
      const id = await authService.getCurrentUserId();
      setCurrentUserId(id);
      socket.emit("set_user_id", { user_id: id });
    };
    fetchCurrentUserId();
  }, []);

  // Load messages when chat is selected
  useEffect(() => {
    const fetchMessages = async () => {
      if (selectedChat && currentUserId) {
        try {
          const fetchedMessages = await userService.getMessages(
            selectedChat.id
          );
          const formattedMessages = fetchedMessages.map((msg) => ({
            ...msg,
            isOwn: msg.sender_id === currentUserId,
          }));
          setMessages(formattedMessages);
          messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
        } catch (error) {
          console.error("Error fetching messages:", error);
        }
      }
    };

    fetchMessages();
  }, [selectedChat, currentUserId]);

  // Handle new messages via socket
  useEffect(() => {
    const handleNewMessage = (msg) => {
      if (
        selectedChat &&
        (msg.sender_id === selectedChat.members[1].supertokens_id ||
          msg.sender_id === selectedChat.members[0].supertokens_id)
      ) {
        setMessages((prevMessages) => [
          ...prevMessages,
          {
            ...msg,
            isOwn: msg.sender_id === currentUserId,
          },
        ]);
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
      }
    };

    if (socket) {
      socket.on("new_message", handleNewMessage);
    }

    return () => {
      if (socket) {
        socket.off("new_message", handleNewMessage);
      }
    };
  }, [selectedChat, currentUserId]);

  const handleSendMessage = async (text) => {
    if (!selectedChat || !currentUserId) return;

    try {
      const recipientId = selectedChat.members.find(
        (member) => member.supertokens_id !== currentUserId
      )?.supertokens_id;

      if (!recipientId) {
        console.error("Recipient not found");
        return;
      }

      const response = await userService.sendMessage(selectedChat.id, text);

      const newMessage = {
        id: response?.id || Date.now(),
        content: text,
        sender_id: currentUserId,
        created_at: new Date().toISOString(),
        isOwn: true,
      };

      setMessages((prevMessages) => [...prevMessages, newMessage]);
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });

      socket.emit("message", {
        recipient_id: recipientId,
        message: text,
      });
    } catch (error) {
      console.error("Error sending message:", error);
    }
  };

  return (
    <div className="relative flex flex-col w-3/4 h-screen">
      <div className="absolute inset-0 bg-[url('/images/background.png')] bg-cover bg-center opacity-50"></div>
      {selectedChat && <MessageHeader />}
      <div
        className="relative flex flex-col flex-1 w-2/3 mx-auto mb-20 px-14 my-3 overflow-y-auto custom-scrollbar"
        style={{ justifyContent: "flex-end" }}
      >
        {messages.map((msg, index) => (
          <div
            key={msg.id || `${msg.sender_id}-${msg.created_at}-${index}`}
            className={`flex w-full ${
              msg.isOwn ? "justify-end" : "justify-start"
            }`}
          >
            <p
              className={`rounded-md my-1 py-1 px-2 max-w-xs ${
                msg.isOwn ? "bg-blue-500 text-white" : "bg-gray-300 text-black"
              }`}
              style={{ wordBreak: "break-word", overflowWrap: "break-word" }}
            >
              {msg.content}
            </p>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      {selectedChat && <MessageInput onSendMessage={handleSendMessage} />}
    </div>
  );
}

function MessageInput({ onSendMessage }) {
  const [input, setInput] = useState("");
  const inputRef = useRef(null);

  useEffect(() => {
    inputRef.current.focus();
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input.trim()) {
      onSendMessage(input);
      setInput("");
      inputRef.current.focus();
    }
  };

  return (
    <form
      className="absolute bottom-0 left-0 right-0 flex justify-center p-6 border-gray-300"
      onSubmit={handleSubmit}
    >
      <input
        ref={inputRef}
        className="w-1/2 p-2 mr-2 border border-gray rounded-md"
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        placeholder="Type your message..."
      />
      <button type="submit" className="flex items-center">
        <IoSend className="self-center w-10 h-10 text-blue-500 hover:text-blue-700" />
      </button>
    </form>
  );
}

export default MessageWindow;
