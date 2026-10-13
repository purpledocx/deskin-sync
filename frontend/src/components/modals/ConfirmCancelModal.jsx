export default function ConfirmCancelModal({ spaceName, when, loading, error, onClose, onConfirm }) {
  return (
    <div onClick={onClose} className="fixed inset-0 z-10 flex items-center justify-center bg-black/40 p-4">
      <div
        onClick={(e) => e.stopPropagation()}
        className="flex w-full max-w-md flex-col gap-4 rounded-form bg-white p-6 shadow-hover"
      >
        <h2 className="text-2xl font-semibold text-navy">Cancel booking?</h2>
        <p className="text-sm text-chip">
          {spaceName}, {when}. Bookings will stay visible in your list as Cancelled.
        </p>

        {error && (
          <div className="rounded-form border border-bad bg-bad-soft px-3 py-2 text-sm text-bad-ink">{error}</div>
        )}

        <div className="flex gap-3">
          <button type="button" onClick={onClose} className="btn btn-secondary flex-1">Back</button>
          <button type="button" onClick={onConfirm} disabled={loading} className="btn btn-danger flex-1">
            {loading ? "Cancelling..." : "Cancel booking"}
          </button>
        </div>
      </div>
    </div>
  );
}