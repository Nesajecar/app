import React, { useState, useEffect } from 'react';
import { adminAPI, dogsAPI } from '../services/api';

const AdminPanel = () => {
  const [pendingDogs, setPendingDogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchPendingDogs();
  }, []);

  const fetchPendingDogs = async () => {
    try {
      setLoading(true);
      const response = await adminAPI.getPendingDogs();
      setPendingDogs(response.data);
      setError('');
    } catch (err) {
      setError('Greška pri učitavanju pasa');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleConfirm = async (id) => {
    if (!window.confirm('Potvrdite da je pas zaista spašen?')) {
      return;
    }

    try {
      await adminAPI.confirmRescue(id);
      setSuccess('Spašavanje potvrđeno');
      fetchPendingDogs();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška pri potvrdi');
    }
  };

  const handleReject = async (id) => {
    if (!window.confirm('Odbijate spašavanje? Pas će biti vraćen u status "Prijavljen".')) {
      return;
    }

    try {
      await adminAPI.rejectRescue(id);
      setSuccess('Spašavanje odbijeno');
      fetchPendingDogs();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška pri odbijanju');
    }
  };

  const getStatusLabel = (status) => {
    const labels = {
      reported: 'Prijavljen',
      pending_admin: 'Čeka potvrdu',
      confirmed: 'Potvrđen',
      removed: 'Uklonjen',
    };
    return labels[status] || status;
  };

  if (loading) {
    return <div className="container"><div className="loading">Učitavanje...</div></div>;
  }

  return (
    <div className="container">
      <div className="card">
        <h2>Admin panel - Psi koji čekaju potvrdu</h2>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        {pendingDogs.length === 0 ? (
          <p>Nema pasa koji čekaju potvrdu.</p>
        ) : (
          <div className="grid">
            {pendingDogs.map((dog) => (
              <div key={dog.id} className="card">
                <h3>{dog.title}</h3>
                <p style={{ color: '#666', marginBottom: '10px' }}>
                  {dog.description || 'Nema opisa'}
                </p>
                <p style={{ fontSize: '14px', color: '#888' }}>
                  📍 {dog.latitude.toFixed(4)}, {dog.longitude.toFixed(4)}
                </p>
                <span className={`status-badge status-${dog.status}`}>
                  {getStatusLabel(dog.status)}
                </span>
                {dog.picked_up_by && (
                  <p style={{ marginTop: '10px', fontSize: '14px' }}>
                    Spašio: {dog.picked_up_by.full_name}
                  </p>
                )}
                {dog.images && dog.images.length > 0 && dog.images[0] && dog.images[0].url && (
                  <img
                    src={dog.images[0].url.startsWith('http') ? dog.images[0].url : `http://localhost:8000${dog.images[0].url}`}
                    alt={dog.title}
                    className="dog-image"
                    style={{ maxHeight: '200px', marginTop: '10px' }}
                  />
                )}
                <div style={{ marginTop: '15px', display: 'flex', gap: '10px' }}>
                  <button
                    onClick={() => handleConfirm(dog.id)}
                    className="btn btn-success btn-small"
                  >
                    Potvrdi
                  </button>
                  <button
                    onClick={() => handleReject(dog.id)}
                    className="btn btn-danger btn-small"
                  >
                    Odbij
                  </button>
                  <a
                    href={`/dogs/${dog.id}`}
                    className="btn btn-secondary btn-small"
                  >
                    Detalji
                  </a>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminPanel;
