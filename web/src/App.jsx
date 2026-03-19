import { useState, useEffect, useCallback } from 'react';
import { Routes, Route, useNavigate } from 'react-router-dom';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import SearchableDropdown from './components/SearchableDropdown';
import OSSelector from './components/OSSelector';
import SummaryPanel from './components/SummaryPanel';
import { ConfirmModal, CreatingModal } from './components/Modal';
import ToastContainer from './components/Toast';
import VmDetails from './components/VmDetails';
import './App.css';

const API_BASE_URL = `http://100.119.100.4:8000`;

// ─── Helpers ───
function isWindowsTemplate(name) {
  return name ? name.toLowerCase().includes('win') : false;
}

function formatDateDisplay(dateStr) {
  if (!dateStr) return '—';
  try {
    const d = new Date(dateStr + 'T00:00:00');
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric' });
  } catch { return dateStr; }
}

function generateUUID() {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return crypto.randomUUID();
  }
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    const r = Math.random() * 16 | 0;
    const v = c === 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function dateOffset(days) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().split('T')[0];
}

const today = dateOffset(0);
const maxDate = (() => { const d = new Date(); d.setMonth(d.getMonth() + 1); return d.toISOString().split('T')[0]; })();

export default function App() {
  const navigate = useNavigate();

  // ─── Data from API ───
  const [folders, setFolders] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [portgroups, setPortgroups] = useState([]);
  const [vmCache, setVmCache] = useState([]);
  const [loadingFolders, setLoadingFolders] = useState(false);
  const [loadingTemplates, setLoadingTemplates] = useState(false);
  const [loadingPortgroups, setLoadingPortgroups] = useState(false);

  // ─── Form state ───
  const [vmName, setVmName] = useState('');
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [selectedPortgroup, setSelectedPortgroup] = useState(null);
  const [selectedTemplate, setSelectedTemplate] = useState(null);
  const [selectedOS, setSelectedOS] = useState('ubuntu');
  const [diskSize, setDiskSize] = useState(50);
  const [ramSize, setRamSize] = useState(4096);
  const [cpuCores, setCpuCores] = useState(4);
  const [shutdownDate, setShutdownDate] = useState(dateOffset(7));
  const [deletionDate, setDeletionDate] = useState(dateOffset(10));

  // ─── UI state ───
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [showCreating, setShowCreating] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [pendingMoid, setPendingMoid] = useState(null);
  const [toasts, setToasts] = useState([]);

  // ─── Toast helper ───
  const addToast = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    setToasts(prev => [...prev, { id, message, type }]);
  }, []);

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id));
  }, []);

  // ─── Data fetching ───
  const fetchVMCache = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/vm-cache`);
      const data = await res.json();
      setVmCache(data.vms || []);
    } catch (e) {
      console.error('Failed to load VM cache:', e);
    }
  }, []);

  useEffect(() => {
    async function loadData() {
      // Folders
      setLoadingFolders(true);
      try {
        const res = await fetch(`${API_BASE_URL}/list-folders`);
        const data = await res.json();
        setFolders(data.folders || []);
      } catch (e) { console.error('Folders:', e); }
      setLoadingFolders(false);

      // Templates
      setLoadingTemplates(true);
      try {
        const res = await fetch(`${API_BASE_URL}/list-templates`);
        const data = await res.json();
        setTemplates(data.templates || []);
      } catch (e) { console.error('Templates:', e); }
      setLoadingTemplates(false);

      // Portgroups
      setLoadingPortgroups(true);
      try {
        const res = await fetch(`${API_BASE_URL}/list-portgroups`);
        const data = await res.json();
        setPortgroups(data.portgroups || []);
      } catch (e) { console.error('Portgroups:', e); }
      setLoadingPortgroups(false);

      // VM Cache
      fetchVMCache();
    }
    loadData();
  }, [fetchVMCache]);

  // ─── Filtered templates based on OS ───
  const filteredTemplates = selectedOS === 'windows'
    ? templates.filter(t => isWindowsTemplate(t.name))
    : templates.filter(t => !isWindowsTemplate(t.name));

  // ─── Resolve names for summary ───
  const folderName = folders.find(f => f.code === selectedFolder)?.name;
  const portgroupName = portgroups.find(p => p.code === selectedPortgroup)?.name;
  const templateName = filteredTemplates.find(t => t.code === selectedTemplate)?.name
    || templates.find(t => t.code === selectedTemplate)?.name;

  // ─── OS change → select template accordingly ───
  const handleOSChange = (os) => {
    setSelectedOS(os);
    if (os === 'ubuntu') {
      const ubuntuTemplate = templates.find(t => !isWindowsTemplate(t.name));
      if (ubuntuTemplate) {
        setSelectedTemplate(ubuntuTemplate.code);
      } else {
        setSelectedTemplate(null);
      }
    } else {
      setSelectedTemplate(null);
    }
  };

  // ─── CPU options ───
  const cpuOptions = Array.from({ length: 32 }, (_, i) => i + 1);

  // ─── Handle Create click ───
  const handleCreateClick = () => {
    if (!vmName.trim()) { addToast('Please enter a VM name.', 'error'); return; }
    if (!selectedFolder) { addToast('Please select a folder.', 'error'); return; }
    if (!selectedTemplate) { addToast('Please select a template.', 'error'); return; }
    setShowConfirm(true);
  };

  const confirmDetails = [
    { label: 'VM Name', value: vmName },
    { label: 'Folder', value: folderName || '—' },
    { label: 'Portgroup / VLAN', value: portgroupName || '—' },
    { label: 'Template / OS', value: templateName || '—' },
    { label: 'Disk', value: `${diskSize} GB` },
    { label: 'RAM', value: `${ramSize} MB` },
    { label: 'CPU', value: `${cpuCores} Core${cpuCores > 1 ? 's' : ''}` },
    { label: 'Shutdown', value: formatDateDisplay(shutdownDate) },
    { label: 'Deletion', value: formatDateDisplay(deletionDate) },
  ];

  // ─── VM Creation flow ───
  const handleConfirmCreate = async () => {
    if (isCreating) return;
    setIsCreating(true);
    setShowConfirm(false);
    setShowCreating(true);
    setPendingMoid(null);

    const txUuid = generateUUID();

    try {
      // Step 1: Start Create VM via RabbitMQ (Returns immediately)
      const createRes = await fetch(`${API_BASE_URL}/vm`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          vm_name: vmName.trim(),
          folder: folderName || '',
          template: templateName || '',
          portgroup: portgroups.find(p => p.code === selectedPortgroup)?.code || '',
          is_windows_image: isWindowsTemplate(templateName) ? 'true' : 'false',
          ram_size: parseInt(ramSize) || 4096,
          cpu_number: parseInt(cpuCores) || 1,
          disk_size_gb: [parseInt(diskSize) || 50],
          owner: 'WebPortal-User',
          shutdown_date: new Date(shutdownDate).toISOString(),
          deletion_date: new Date(deletionDate).toISOString(),
          transaction_uuid: txUuid,
        }),
      });

      if (!createRes.ok) {
        const errData = await createRes.json();
        throw new Error(errData.detail || 'Failed to queue VM creation');
      }

      // Step 2: Poll Database for Provisioning Progress
      // We poll until we get a "real" MOID (not starting with 'pending-')
      let realMoidFound = false;
      // Terraform can take up to 2-3 minutes, so 1.5s * 120 = 180s
      for (let i = 0; i < 120; i++) {
        await new Promise(r => setTimeout(r, 1500));
        try {
          const checkRes = await fetch(`${API_BASE_URL}/check_provisioning/${txUuid}`);
          if (checkRes.ok) {
            const checkData = await checkRes.json();
            if (checkData.exists) {
              const currentMoid = checkData.vcenter_uuid;
              setPendingMoid(currentMoid);
              
              // If it's a real MOID, we are done
              if (currentMoid && !currentMoid.startsWith('pending-')) {
                realMoidFound = true;
                break;
              }
              
              // If it's the first time we see the pending record, refresh sidebar once
              if (i % 5 === 0) await fetchVMCache(); 
            }
          }
        } catch { /* ignore network error while polling */ }
      }

      if (realMoidFound) {
        addToast(`Provisioning complete for VM: ${vmName}.`, 'success');
        await fetchVMCache();
        // We keep the modal open so the user can click "View VM Details"
      } else {
        // If we timed out but it's still pending, at least the user has the 'pending' link
        if (!pendingMoid) {
            throw new Error("Provisioning timed out or record not found.");
        }
      }

    } catch (error) {
      setShowCreating(false);
      addToast(`Execution failure for ${vmName}. Detail: ${error.message || error}`, 'error');
      setIsCreating(false);
      setPendingMoid(null);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <>
      <Navbar onToggleSidebar={() => setSidebarCollapsed(!sidebarCollapsed)} />
      <Sidebar vms={vmCache} collapsed={sidebarCollapsed} />

      <div className={`main-wrapper ${sidebarCollapsed ? 'sidebar-hidden' : ''}`}>
        <Routes>
          <Route path="/" element={
            <>
              <div className="main-content">
                {/* Card: General Info */}
                <div className="card">
                  <div className="card-title">General Info</div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="input-vm-name">VM Name:</label>
                    <input
                      type="text"
                      className="form-input"
                      id="input-vm-name"
                      placeholder="Enter VM name"
                      autoComplete="off"
                      value={vmName}
                      onChange={e => setVmName(e.target.value)}
                    />
                  </div>
                  <SearchableDropdown
                    label="Folder / Project"
                    options={folders}
                    value={selectedFolder}
                    onChange={setSelectedFolder}
                    loading={loadingFolders}
                  />
                  <SearchableDropdown
                    label="VLAN / Portgroup"
                    options={portgroups}
                    value={selectedPortgroup}
                    onChange={setSelectedPortgroup}
                    loading={loadingPortgroups}
                  />
                </div>

                {/* Card: OS */}
                <div className="card">
                  <div className="card-title">OS</div>
                  <OSSelector 
                    selectedOS={selectedOS} 
                    onSelect={handleOSChange}
                    templates={filteredTemplates}
                    selectedTemplate={selectedTemplate}
                    onSelectTemplate={setSelectedTemplate}
                  />
                  <SearchableDropdown
                    label="Template"
                    options={filteredTemplates}
                    value={selectedTemplate}
                    onChange={setSelectedTemplate}
                    loading={loadingTemplates}
                  />
                </div>

                {/* Card: Resources */}
                <div className="card">
                  <div className="card-title">Resources</div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="input-disk-size">Disk Size in GB:</label>
                    <input
                      type="number"
                      className="form-input"
                      id="input-disk-size"
                      value={diskSize}
                      min="1"
                      onChange={e => setDiskSize(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label" htmlFor="input-ram-size">RAM Size in MB:</label>
                    <input
                      type="number"
                      className="form-input"
                      id="input-ram-size"
                      value={ramSize}
                      min="512"
                      step="512"
                      onChange={e => setRamSize(e.target.value)}
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Number of CPU Cores:</label>
                    <div className="select-wrapper">
                      <select
                        className="form-select"
                        value={cpuCores}
                        onChange={e => setCpuCores(parseInt(e.target.value))}
                      >
                        {cpuOptions.map(n => (
                          <option key={n} value={n}>{n} Core{n > 1 ? 's' : ''}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                </div>

                {/* Card: Scheduling */}
                <div className="card">
                  <div className="card-title">Scheduling</div>
                  <div className="form-two-col">
                    <div className="form-group">
                      <label className="form-label" htmlFor="date-shutdown">Shutdown date:</label>
                      <input
                        type="date"
                        className="form-date"
                        id="date-shutdown"
                        value={shutdownDate}
                        min={today}
                        max={maxDate}
                        onChange={e => setShutdownDate(e.target.value)}
                      />
                    </div>
                    <div className="form-group">
                      <label className="form-label" htmlFor="date-deletion">Deletion date:</label>
                      <input
                        type="date"
                        className="form-date"
                        id="date-deletion"
                        value={deletionDate}
                        min={today}
                        max={maxDate}
                        onChange={e => setDeletionDate(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Summary Panel */}
              <SummaryPanel
                vmName={vmName}
                folderName={folderName}
                portgroupName={portgroupName}
                templateName={templateName}
                diskSize={diskSize}
                ramSize={ramSize}
                cpuLabel={`${cpuCores} Core${cpuCores > 1 ? 's' : ''}`}
                shutdownDate={shutdownDate}
                deletionDate={deletionDate}
                onCreateClick={handleCreateClick}
              />
            </>
          } />

          <Route path="/vm/:moid" element={
            <div className="main-content" style={{ maxWidth: '1200px', margin: '0 auto', flex: 1 }}>
              <VmDetails />
            </div>
          } />
        </Routes>
      </div>

      {/* Modals */}
      <ConfirmModal
        visible={showConfirm}
        details={confirmDetails}
        onCancel={() => setShowConfirm(false)}
        onConfirm={handleConfirmCreate}
      />
      <CreatingModal visible={showCreating} pendingMoid={pendingMoid} onClose={() => setShowCreating(false)} />

      {/* Toasts */}
      <ToastContainer toasts={toasts} onRemove={removeToast} />
    </>
  );
}
