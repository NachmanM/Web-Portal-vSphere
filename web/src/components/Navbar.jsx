import { Link, useLocation } from 'react-router-dom';
import './Navbar.css';

export default function Navbar({ onToggleSidebar }) {
    const location = useLocation();
    
    // Determine active tabs using location path
    const isCreateActive = location.pathname === '/';
    const isDetailsActive = location.pathname.startsWith('/vm/');

    return (
        <nav className="navbar">
            <div className="navbar-left">
                <button className="navbar-toggle" onClick={onToggleSidebar} title="Toggle sidebar">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                        <line x1="3" y1="6" x2="21" y2="6" />
                        <line x1="3" y1="12" x2="21" y2="12" />
                        <line x1="3" y1="18" x2="21" y2="18" />
                    </svg>
                </button>
                <div className="navbar-brand">vCenter <span>Web Portal</span></div>
            </div>
            <ul className="navbar-links">
                <li><Link to="/" className={isCreateActive ? "active" : ""}>CreateVM</Link></li>
                <li><Link to="#">Dashboard</Link></li>
                <li><Link to="#">Products</Link></li>
                <li><Link to={location.pathname.startsWith('/vm/') ? location.pathname : '#'} className={isDetailsActive ? "active" : ""}>DetailsVM</Link></li>
            </ul>
            <div className="navbar-right">
                <div className="navbar-avatar">U</div>
            </div>
        </nav>
    );
}
