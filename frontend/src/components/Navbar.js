import React, { useContext } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';
import './Navbar.css';

const Navbar = () => {
  const { user, logout } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-brand">
          🐕 Dog Rescue
        </Link>
        
        <div className="navbar-links">
          <Link to="/dogs">Psi</Link>
          
          {user ? (
            <>
              <Link to="/dogs/create">Prijavi psa</Link>
              <Link to="/profile">Profil</Link>
              {user.is_admin && (
                <Link to="/admin">Admin</Link>
              )}
              <button onClick={handleLogout} className="btn-logout">
                Odjavi se
              </button>
            </>
          ) : (
            <>
              <Link to="/login">Prijavi se</Link>
              <Link to="/signup">Registruj se</Link>
            </>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Navbar;
