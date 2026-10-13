const pad = (n) => String(n).padStart(2, "0");

// API may return naive datetimes (no "Z"): they are UTC
export const parseApiDate = (iso) =>
  new Date(/(Z|[+-]\d{2}:?\d{2})$/.test(iso) ? iso : `${iso}Z`);

export const formatDateTime = (iso) => {
  const d = parseApiDate(iso);
  return `${pad(d.getDate())}.${pad(d.getMonth() + 1)}.${d.getFullYear()} ${pad(d.getHours())}:${pad(d.getMinutes())}`;
};

// Date -> "YYYY-MM-DDTHH:mm" for <input type="datetime-local">
export const toLocalInput = (d) =>
  `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}T${pad(d.getHours())}:${pad(d.getMinutes())}`;