import React, { useState, useContext } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { AuthContext } from '../context/AuthContext';

const Signup = () => {
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { signup, login } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    const signupResult = await signup(email, password, fullName);
    
    if (signupResult.success) {
      // Automatski prijavi korisnika nakon registracije
      const loginResult = await login(email, password);
      if (loginResult.success) {
        navigate('/dogs');
      } else {
        setError('Registracija uspešna, ali greška pri prijavi. Molimo prijavite se ručno.');
      }
    } else {
      setError(signupResult.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '400px', margin: '50px auto' }}>
        <h2>Registruj se</h2>
        
        {error && <div className="alert alert-error">{error}</div>}
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Ime i prezime</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              placeholder="Marko Marković"
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="tvoj@email.com"
            />
          </div>

          <div className="form-group">
            <label>Lozinka</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="••••••••"
              minLength="2"
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Registracija...' : 'Registruj se'}
          </button>
        </form>

        <p style={{ marginTop: '20px', textAlign: 'center' }}>
          Već imaš nalog? <Link to="/login">Prijavi se</Link>
        </p>
      </div>
    </div>
  );
};

export default Signup;
