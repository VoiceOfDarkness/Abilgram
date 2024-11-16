// import React, { useEffect, useState } from "react";
// import io from "socket.io-client";

// // Подключаемся к серверу
// const socket = io("http://localhost:8000");

// function Chat() {
//   const [messages, setMessages] = useState([]);
//   const [input, setInput] = useState("");

//   useEffect(() => {
//     // Обработка события при получении сообщения
//     socket.on("message", (data) => {
//       setMessages((prevMessages) => [...prevMessages, data]);
//     });

//     return () => {
//       socket.off("message");
//     };
//   }, []);

//   const sendMessage = () => {
//     // Отправляем сообщение на сервер
//     socket.emit("message", { msg: input });
//     setInput("");
//   };

//   return (
//     <div>
//       <h2>Chat</h2>
//       <div>
//         {messages.map((message, index) => (
//           <p key={index}>{message.msg}</p>
//         ))}
//       </div>
//       <input
//         placeholder="Message"
//         value={input}
//         onChange={(e) => setInput(e.target.value)}
//       />
//       <button onClick={sendMessage}>Send</button>
//     </div>
//   );
// }

// export default Chat;
