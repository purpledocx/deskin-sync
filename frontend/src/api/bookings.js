import { request } from "./client";

const toBody = ({ spaceId, start, end }) => ({
  space_id: spaceId,
  start_at: new Date(start).toISOString(),
  end_at: new Date(end).toISOString(),
});

// trailing "/" matters: without it FastAPI redirects
export const getBookings = () => request("/bookings/");
export const createBooking = (data) =>
  request("/bookings/", { method: "POST", body: toBody(data) });
export const updateBooking = (id, data) =>
  request(`/bookings/${id}`, { method: "PUT", body: toBody(data) });
export const cancelBooking = (id) =>
  request(`/bookings/${id}`, { method: "DELETE" });