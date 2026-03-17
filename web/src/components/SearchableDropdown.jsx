import { useState, useRef, useEffect } from 'react';
import './SearchableDropdown.css';

export default function SearchableDropdown({ label, options, value, onChange, placeholder = 'Select option', loading = false }) {
    const [open, setOpen] = useState(false);
    const [search, setSearch] = useState('');
    const ref = useRef(null);
    const searchRef = useRef(null);

    useEffect(() => {
        const handleClick = (e) => {
            if (ref.current && !ref.current.contains(e.target)) setOpen(false);
        };
        document.addEventListener('mousedown', handleClick);
        return () => document.removeEventListener('mousedown', handleClick);
    }, []);

    useEffect(() => {
        if (open && searchRef.current) {
            searchRef.current.focus();
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setSearch('');
        }
    }, [open]);

    const filtered = search
        ? options.filter(o => o.name.toLowerCase().includes(search.toLowerCase()))
        : options;

    const selectedItem = options.find(o => o.code === value);

    const handleSelect = (item) => {
        onChange(item.code);
        setOpen(false);
    };

    const handleClear = (e) => {
        e.stopPropagation();
        onChange(null);
    };

    return (
        <div className="form-group">
            {label && <label className="form-label">{label}</label>}
            <div className="dropdown-container" ref={ref}>
                <button
                    className={`dropdown-trigger ${open ? 'open' : ''} ${loading ? 'loading' : ''}`}
                    type="button"
                    onClick={() => !loading && setOpen(!open)}
                >
                    {loading ? (
                        <span className="placeholder">Loading...</span>
                    ) : selectedItem ? (
                        <>
                            <span>{selectedItem.name}</span>
                            <span className="trigger-right">
                                <button className="clear-btn" onClick={handleClear} title="Clear">&times;</button>
                                <span className="arrows">▲<br />▼</span>
                            </span>
                        </>
                    ) : (
                        <>
                            <span className="placeholder">{placeholder}</span>
                            <span className="arrows">▲<br />▼</span>
                        </>
                    )}
                </button>

                {open && (
                    <div className="dropdown-panel">
                        <input
                            ref={searchRef}
                            type="text"
                            className="dropdown-search"
                            placeholder="🔍 Filter..."
                            value={search}
                            onChange={e => setSearch(e.target.value)}
                        />
                        <div className="dropdown-options">
                            {filtered.length === 0 ? (
                                <div className="dropdown-option no-results">No options available</div>
                            ) : (
                                filtered.map(item => (
                                    <div
                                        key={item.code}
                                        className={`dropdown-option ${item.code === value ? 'selected' : ''}`}
                                        onClick={() => handleSelect(item)}
                                    >
                                        {item.name}
                                    </div>
                                ))
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
