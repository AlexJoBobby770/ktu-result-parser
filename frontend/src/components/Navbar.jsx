import "./Navbar.css";

function Navbar({ currentUser, backendStatus, onLogout }) {
  return (
    <nav className="nav">
      <div className="nav-container">
        <div className="nav-logo">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="currentColor" strokeWidth="2" />
            <path
              d="M12 16L15 19L20 13"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>
          <span>KTU Processor</span>
        </div>
        <div className="nav-status">
          <span className="nav-user">Hi, {currentUser}</span>
          <span className={`status-indicator ${backendStatus}`}></span>
          <span className="status-text">
            {backendStatus === "connected" && "Online"}
            {backendStatus === "disconnected" && "Offline"}
            {backendStatus === "checking" && "Connecting"}
          </span>
          <button className="btn-logout" onClick={onLogout}>
            Logout
          </button>
        </div>
      </div>
    </nav>
  );
}

export default Navbar;