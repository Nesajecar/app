import React, { useState, useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { authAPI } from '../services/api';

const Profile = () => {
  const { user, updateUser } = useContext(AuthContext);
  const [fullName, setFullName] = useState(user?.full_name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleUpdate = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await authAPI.updateProfile({
        full_name: fullName,
        email: email,
      });
      updateUser(response.data);
      setSuccess('Profil uspešno ažuriran');
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška pri ažuriranju profila');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!window.confirm('Da li ste sigurni da želite da obrišete nalog? Ova akcija je nepovratna.')) {
      return;
    }

    setDeleting(true);
    try {
      await authAPI.deleteAccount();
      window.location.href = '/';
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška pri brisanju naloga');
      setDeleting(false);
    }
  };

  if (!user) {
    return <div className="container"><div className="loading">Učitavanje...</div></div>;
  }

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '500px', margin: '20px auto' }}>
        <h2>Moj profil</h2>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <form onSubmit={handleUpdate}>
          <div className="form-group">
            <label>Ime i prezime</label>
            <input
              type="text"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
          </div>

          <div className="form-group">
            <label>Status</label>
            <input
              type="text"
              value={user.is_admin ? 'Administrator' : 'Korisnik'}
              disabled
              style={{ backgroundColor: '#f5f5f5' }}
            />
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%', marginBottom: '15px' }}
            disabled={loading}
          >
            {loading ? 'Čuvanje...' : 'Sačuvaj izmene'}
          </button>
        </form>

        <div style={{ marginTop: '30px', paddingTop: '20px', borderTop: '1px solid #ddd' }}>
          <h3 style={{ color: '#dc3545', marginBottom: '15px' }}>Opasna zona</h3>
          <button
            onClick={handleDelete}
            className="btn btn-danger"
            disabled={deleting}
          >
            {deleting ? 'Brisanje...' : 'Obriši nalog'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Profile;
