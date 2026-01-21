import React from "react";
import "./navbar.css";

const Navbar = ({ setPage }) => {
  return (
    <nav className="navbar">
      <div className="nav-container">
        <div
          className="nav-logo"
          onClick={() => setPage("home")}
          style={{ cursor: "pointer" }}
        >
          Type-Id
        </div>

        <div className="nav-links">
          <button
            className="nav-btn"
            onClick={() => setPage("signin")}   
          >
            Sign In
          </button>

          <button
            className="nav-btn signup"
            onClick={() => setPage("signup")}
          >
            Sign Up
          </button>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
