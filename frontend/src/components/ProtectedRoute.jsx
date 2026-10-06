import { Navigate } from "react-router-dom";
import { getToken } from "../api/client";

// if no token --> readdress to login page
export default function ProtectedRoute({ children }) {
  return getToken() ? children : <Navigate to="/register?mode=login" replace />;
}