import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import './VmDetails.css';

const API_BASE_URL = `http://100.119.100.4:8000`;

export default function VmDetails() {
  const { moid } = useParams();
  const [vmInfo, setVmInfo] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchDetails() {
      setLoading(true);
      setError(null);
      try {
        const res = await fetch(`${API_BASE_URL}/vm_info/${encodeURIComponent(moid)}`);
        const data = await res.json();
        if (data.status === 'success') {
          setVmInfo(data.vm_info);
        } else {
          setError(data.error || data.detail || 'Failed to fetch details');
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchDetails();
  }, [moid]);

  if (loading) return <div className="vm-details-loading">Loading VM details...</div>;
  if (error) return <div className="vm-details-error">Error: {error}</div>;
  if (!vmInfo) return null;

  return (
    <div className="vm-details-container">
      <div className="vm-details-header">
        <h2>💻 {vmInfo.name || moid}</h2>
      </div>
      
      <div className="vm-details-grid">
        <div className="card">
          <div className="card-title">Virtual Machine Details</div>
          <div className="details-table" style={{ borderTop: '2px solid #0b7593', paddingTop: '15px' }}>
            <div className="detail-row">
              <span className="detail-label">Power Status</span>
              <span className="detail-value">
                <span className={`status-dot ${vmInfo.state?.toLowerCase() === 'poweredon' ? 'on' : 'off'}`} />
                {vmInfo.state === 'poweredOn' ? 'Powered On' : vmInfo.state}
              </span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Guest OS</span>
              <span className="detail-value">{vmInfo.os || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">IP Address</span>
              <span className="detail-value highlight">{vmInfo.ip_address || 'Waiting for DHCP...'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Owner</span>
              <span className="detail-value">{vmInfo.owner || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Created</span>
              <span className="detail-value">{vmInfo.created_date ? new Date(vmInfo.created_date).toLocaleString() : 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Shutdown</span>
              <span className="detail-value">{vmInfo.shutdown_date ? new Date(vmInfo.shutdown_date).toLocaleDateString() : 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Deletion</span>
              <span className="detail-value">{vmInfo.deletion_date ? new Date(vmInfo.deletion_date).toLocaleDateString() : 'N/A'}</span>
            </div>
          </div>
        </div>

        {/* If VM exists physically, show hardware */}
        {vmInfo.cpu_count !== undefined && (
          <div className="card">
            <div className="card-title">VM Hardware</div>
            <div className="details-table" style={{ borderTop: '2px solid #e0e0e0', paddingTop: '15px' }}>
              <div className="detail-row">
                <span className="detail-label">CPU</span>
                <span className="detail-value">{vmInfo.cpu_count} vCPU</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Memory</span>
                <span className="detail-value">{vmInfo.ram_gb} GB</span>
              </div>
              {vmInfo.disks && vmInfo.disks.map((d, i) => (
                <div className="detail-row" key={i}>
                  <span className="detail-label">{d.label || `Disk ${i+1}`}</span>
                  <span className="detail-value">{d.capacity_gb} GB</span>
                </div>
              ))}
              {vmInfo.networks && vmInfo.networks.map((n, i) => (
                <div className="detail-row" key={i}>
                  <span className="detail-label">Network {i+1}</span>
                  <span className="detail-value">{n.name} {n.vlan !== 'Unknown' ? `(${n.vlan})` : ''}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="card">
          <div className="card-title">Related Objects</div>
          <div className="details-table" style={{ borderTop: '2px solid #e0e0e0', paddingTop: '15px' }}>
            {vmInfo.host && (
              <div className="detail-row">
                <span className="detail-label">ESXi Host</span>
                <span className="detail-value">{vmInfo.host}</span>
              </div>
            )}
            <div className="detail-row">
              <span className="detail-label">Folder</span>
              <span className="detail-value">{vmInfo.folder || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">MOID</span>
              <span className="detail-value">{vmInfo.moid || moid}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
