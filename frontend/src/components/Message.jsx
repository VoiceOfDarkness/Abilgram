import React from "react";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import getImageUrl from "@/helpers/imageUrl";
import { formatMessageTime } from "@/helpers/formatTime";

const Message = ({ message, sender }) => {
  const isOwn = message.isOwn;

  return (
    <div
      className={`flex w-full items-end gap-2 my-2 ${
        isOwn ? "flex-row-reverse" : "flex-row"
      }`}
    >
      <Avatar className="w-8 h-8 flex-shrink-0">
        <AvatarImage
          src={getImageUrl(sender?.avatar_url)}
          alt={sender?.username || "User avatar"}
        />
        <AvatarFallback className="bg-cyan-950">
          {sender?.username?.slice(0, 2).toUpperCase()}
        </AvatarFallback>
      </Avatar>

      <div className={`flex flex-col ${isOwn ? "items-end" : "items-start"}`}>
        <span className="text-xs text-gray-500 mb-1">
          {sender?.username} • {formatMessageTime(message.created_at)}
        </span>
        <p
          className={`rounded-2xl py-2 px-4 max-w-xs ${
            isOwn
              ? "bg-blue-500 text-white rounded-br-sm"
              : "bg-gray-300 text-black rounded-bl-sm"
          }`}
          style={{ wordBreak: "break-word", overflowWrap: "break-word" }}
        >
          {message.content}
        </p>
      </div>
    </div>
  );
};

export default Message;
