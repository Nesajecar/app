import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { dogsAPI } from '../services/api';

const DogsList = () => {
  const [dogs, setDogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    fetchDogs();
  }, [statusFilter]);

  const fetchDogs = async () => {
    try {
      setLoading(true);
      const params = statusFilter ? { status: statusFilter } : {};
      const response = await dogsAPI.getAll(params);
      setDogs(response.data);
      setError('');
    } catch (err) {
      setError('Greška pri učitavanju pasa');
      console.error(err);
    } finally {
      setLoading(false);
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
    return <div className="container"><div className="loading">Učitavanje pasa...</div></div>;
  }

  return (
    <div className="container">
      <div className="card">
        <h2>Prijavljeni psi</h2>

        <div style={{ marginBottom: '20px' }}>
          <label style={{ marginRight: '10px' }}>Filter po statusu:</label>
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            style={{ padding: '8px', borderRadius: '5px', border: '1px solid #ddd' }}
          >
            <option value="">Svi</option>
            <option value="reported">Prijavljen</option>
            <option value="pending_admin">Čeka potvrdu</option>
            <option value="confirmed">Potvrđen</option>
          </select>
        </div>

        {error && <div className="alert alert-error">{error}</div>}

        {dogs.length === 0 ? (
          <p>Nema prijavljenih pasa.</p>
        ) : (
          <div className="grid">
            {dogs.map((dog) => (
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
                {dog.images && dog.images.length > 0 && dog.images[0] && dog.images[0].url && (
                  <img
                    src={dog.images[0].url.startsWith('http') ? dog.images[0].url : `http://localhost:8000${dog.images[0].url}`}
                    alt={dog.title}
                    className="dog-image"
                    style={{ maxHeight: '200px', marginTop: '10px' }}
                  />
                )}
                <div style={{ marginTop: '15px' }}>
                  <Link to={`/dogs/${dog.id}`} className="btn btn-primary btn-small">
                    Detalji
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default DogsList;
