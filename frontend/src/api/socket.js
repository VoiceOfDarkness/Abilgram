import { io } from "socket.io-client";

const socket = io("http://localhost:8000/chat", {
  transports: ["websocket"],
  autoConnect: true,
  cors: {
    origin: "http://localhost:5173",
  },
});

export default socket;
