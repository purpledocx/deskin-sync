import { Navigate } from "react-router-dom";
import { getUser } from "../api/session";

export default function ProtectedRoute({ children }) {
  return getUser() ? children : <Navigate to="/register?mode=login" replace />;
}