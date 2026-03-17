import './SummaryPanel.css';

export default function SummaryPanel({
    vmName, folderName, portgroupName, templateName,
    diskSize, ramSize, cpuLabel,
    shutdownDate, deletionDate,
    onCreateClick
}) {
    const fmt = (dateStr) => {
        if (!dateStr) return '—';
        try {
            const d = new Date(dateStr + 'T00:00:00');
            return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
        } catch {
            return dateStr;
        }
    };

    return (
        <div className="summary-panel">
            <div className="summary-card">
                <div className="card-title">Summary</div>
                <div className="summary-content">
                    <div className="summary-line"><strong>Name:</strong> <span>{vmName || '—'}</span></div>
                    <div className="summary-line"><strong>Folder:</strong> <span>{folderName || '—'}</span></div>
                    <div className="summary-line"><strong>Portgroup / VLAN:</strong> <span>{portgroupName || '—'}</span></div>
                    <div className="summary-line"><strong>Template / OS:</strong> <span>{templateName || '—'}</span></div>
                    <hr className="summary-divider" />
                    <div className="summary-line"><strong>Disk:</strong> <span>{diskSize}GB</span></div>
                    <div className="summary-line"><strong>RAM:</strong> <span>{ramSize}MB</span></div>
                    <div className="summary-line"><strong>CPU:</strong> <span>{cpuLabel || '—'}</span></div>
                    <hr className="summary-divider" />
                    <div className="summary-line"><strong>Shutdown:</strong> <span>{fmt(shutdownDate)}</span></div>
                    <div className="summary-line"><strong>Deletion:</strong> <span>{fmt(deletionDate)}</span></div>
                </div>
                <button className="btn-create" type="button" onClick={onCreateClick}>Create</button>
            </div>
        </div>
    );
}
