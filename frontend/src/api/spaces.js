import { request } from "./client"

// fetch availability based on local dates
export const getAvailability = (startLocal, endLocal) => {
    // create urlparams with dates in ISO format
    const q = new URLSearchParams({start_at: new Date(startLocal).toISOString(), end_at: new Date(endLocal).toISOString()})
    // return promise with availability data
    return request(`/spaces/availability?${q}`)
}

// existing bookings of one space in time window (times only)
export const getSpaceBookings = (spaceId, startLocal, endLocal) => {
    const q = new URLSearchParams({start_at: new Date(startLocal).toISOString(), end_at: new Date(endLocal).toISOString()})
    return request(`/spaces/${spaceId}/bookings?${q}`)
}