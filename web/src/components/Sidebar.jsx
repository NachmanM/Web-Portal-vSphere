import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Sidebar.css';

export default function Sidebar({ vms, collapsed, onToggle }) {
    const [search, setSearch] = useState('');
    const [openFolders, setOpenFolders] = useState({});
    const navigate = useNavigate();

    // Group VMs by folder
    const folders = {};
    (vms || []).forEach(vm => {
        const f = vm.folder_name || 'Unknown';
        if (!folders[f]) folders[f] = [];
        folders[f].push(vm);
    });

    const folderNames = Object.keys(folders).sort();

    // Filter
    const matchesSearch = (name) => name.toLowerCase().includes(search.toLowerCase());

    const toggleFolder = (name) => {
        setOpenFolders(prev => ({ ...prev, [name]: !prev[name] }));
    };

    const getStatusClass = (state) => {
        if (state === 'poweredOn') return 'on';
        if (state === 'provisioning') return 'provisioning';
        return 'off';
    };

    return (
        <>
            <aside className={`sidebar ${collapsed ? 'collapsed' : ''}`}>
                <div className="sidebar-header">
                    <input
                        type="text"
                        className="sidebar-search"
                        placeholder="🔍 Search VMs..."
                        value={search}
                        onChange={e => setSearch(e.target.value)}
                    />
                </div>
                <div className="sidebar-tree">
                    {folderNames.map(folderName => {
                        const folderVMs = folders[folderName];
                        const visibleVMs = search
                            ? folderVMs.filter(vm => matchesSearch(vm.vm_name))
                            : folderVMs;
                        const folderMatch = matchesSearch(folderName);

                        if (!folderMatch && visibleVMs.length === 0) return null;

                        const isOpen = openFolders[folderName] || (search && visibleVMs.length > 0);

                        return (
                            <div className={`tree-folder ${isOpen ? 'open' : ''}`} key={folderName}>
                                <div className="tree-folder-label" onClick={() => toggleFolder(folderName)}>
                                    <span className="folder-icon">📁</span>
                                    <span>{folderName}</span>
                                    <span className="chevron">▶</span>
                                </div>
                                <div className="tree-children">
                                    {visibleVMs.map(vm => (
                                        <div
                                            className="tree-vm"
                                            key={vm.vm_moid}
                                            onClick={() => {
                                                if (vm.vm_moid && !vm.vm_moid.startsWith('pending-')) {
                                                    navigate(`/vm/${encodeURIComponent(vm.vm_moid)}`);
                                                }
                                            }}
                                        >
                                            <span className={`status-dot ${getStatusClass(vm.power_state)}`} />
                                            <span>{vm.vm_name}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        );
                    })}
                    {folderNames.length === 0 && (
                        <div style={{ color: 'var(--text-muted)', padding: '12px', fontSize: '0.82rem' }}>
                            No VMs loaded
                        </div>
                    )}
                </div>
            </aside>
        </>
    );
}
