import React, { Suspense } from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { ChatProvider } from "./context/ChatContext";
import ProtectedRoute from "@/routes/ProtectedRoute";
import { Toaster } from "./components/ui/toaster";
import Loading from "./components/Loading";

const LoginPage = React.lazy(() => import("./components/Login"));
const RegisterPage = React.lazy(() => import("./components/Register"));
const ChatPage = React.lazy(() => import("./components/ChatPage"));

function App() {
  return (
    <AuthProvider>
      <ChatProvider>
        <Router>
          <Suspense fallback={<Loading />}>
            <Routes>
              <Route
                path="/"
                element={
                  <ProtectedRoute>
                    <ChatPage />
                  </ProtectedRoute>
                }
              />
              <Route path="/login" element={<LoginPage />} />
              <Route path="/register" element={<RegisterPage />} />
              <Route path="*" element={<div>404 Not Found</div>} />
            </Routes>
          </Suspense>
          <Toaster />
        </Router>
      </ChatProvider>
    </AuthProvider>
  );
}

export default App;
