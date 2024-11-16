import useSessionCheck from "@/hooks/useSessionCheck";
import { useAuth } from "@/context/AuthContext";
import Loading from "@/components/Loading";

const ProtectedRoute = ({ children }) => {
  const { isLoggedIn } = useAuth();
  const { isLoading } = useSessionCheck();

  if (isLoading) {
    return <Loading />;
  }

  return children;
};

export default ProtectedRoute;
