import { Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import AuthPage from "./pages/AuthPage";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardPage from "./pages/DashboardPage";
import AppLayout from "./components/AppLayout";
import MyBookingPage from "./pages/MyBookingsPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<HomePage />} />
      <Route path="/register" element={<AuthPage />} />
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/app" element={<DashboardPage />} />
        <Route path="/app/bookings" element={<MyBookingPage />} />
      </Route>
    </Routes>
  );
}