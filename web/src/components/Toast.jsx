import { useEffect } from 'react';
import './Toast.css';

export default function ToastContainer({ toasts, onRemove }) {
    return (
        <div className="toast-container">
            {toasts.map(t => (
                <Toast key={t.id} toast={t} onRemove={onRemove} />
            ))}
        </div>
    );
}

function Toast({ toast, onRemove }) {
    useEffect(() => {
        const timer = setTimeout(() => onRemove(toast.id), 5000);
        return () => clearTimeout(timer);
    }, [toast.id, onRemove]);

    return (
        <div className={`toast ${toast.type}`}>
            {toast.message}
        </div>
    );
}
