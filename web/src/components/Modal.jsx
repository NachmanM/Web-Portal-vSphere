import { Link } from 'react-router-dom';
import './Modal.css';

export function ConfirmModal({ visible, details, onCancel, onConfirm }) {
    if (!visible) return null;

    return (
        <div className="modal-overlay" onClick={onCancel}>
            <div className="modal" onClick={e => e.stopPropagation()}>
                <div className="modal-header">
                    <div className="modal-title">Confirm VM Creation</div>
                    <button className="modal-close" onClick={onCancel}>&times;</button>
                </div>
                <div className="modal-body">
                    {details.map((d, i) => (
                        <div className="confirm-detail" key={i}>
                            <span className="label">{d.label}</span>
                            <span className="value">{d.value}</span>
                        </div>
                    ))}
                </div>
                <div className="modal-footer">
                    <button className="btn btn-secondary" onClick={onCancel}>Cancel</button>
                    <button className="btn btn-primary" onClick={onConfirm}>Confirm &amp; Create</button>
                </div>
            </div>
        </div>
    );
}

export function CreatingModal({ visible, pendingMoid, onClose }) {
    if (!visible) return null;

    return (
        <div className="modal-overlay">
            <div className="modal">
                <div className="creating-content">
                    <div className="spinner" />
                    <div className="creating-text">Creating VM...</div>
                    <div className="creating-sub" style={{ marginBottom: pendingMoid ? '20px' : '0' }}>
                        Terraform is provisioning your virtual machine.<br />
                        This may take a few minutes.
                    </div>
                    {pendingMoid && typeof onClose === 'function' && (
                        <div className="creating-actions" style={{ display: 'flex', gap: '15px', justifyContent: 'center', marginTop: '15px' }}>
                            <button className="btn btn-secondary" onClick={onClose} style={{ padding: '8px 16px' }}>Close Window</button>
                            <Link 
                                to={`/vm/${encodeURIComponent(pendingMoid)}`} 
                                className="btn btn-primary" 
                                onClick={onClose} 
                                style={{ padding: '8px 16px', textDecoration: 'none', display: 'flex', alignItems: 'center' }}
                            >
                                View VM Details
                            </Link>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
