import { request } from "./client";

export const createBooking = ({spaceId, start, end}) =>
    request("/bookings/", {
        method: "POST",
        body: {
            space_id: spaceId,
            start_at: new Date(start).toISOString(),
            end_at: new Date(end).toISOString()
        }, // if not "," --> fastapi will redirect
    })