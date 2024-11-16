import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Session from "supertokens-web-js/recipe/session";
import { useAuth } from "@/context/AuthContext";

const useSessionCheck = () => {
  const [isLoading, setIsLoading] = useState(true);
  const { login, logout } = useAuth();
  const navigate = useNavigate();

  useEffect(() => {
    const checkSession = async () => {
      try {
        const sessionExists = await Session.doesSessionExist();
        if (sessionExists) {
          login();
        } else {
          logout();
          navigate("/login");
        }
      } catch (error) {
        console.error("Session check error:", error);
        navigate("/login");
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, [login, logout, navigate]);

  return { isLoading };
};

export default useSessionCheck;
