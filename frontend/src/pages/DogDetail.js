import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';
import { dogsAPI } from '../services/api';

const DogDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const [dog, setDog] = useState(null);
  const [images, setImages] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDog();
    fetchImages();
  }, [id]);

  const fetchDog = async () => {
    try {
      const response = await dogsAPI.getById(id);
      setDog(response.data);
      setError('');
    } catch (err) {
      setError('Greška pri učitavanju psa');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchImages = async () => {
    try {
      const response = await dogsAPI.getImages(id);
      setImages(response.data);
    } catch (err) {
      console.error(err);
    }
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    if (!user) {
      setError('Morate biti prijavljeni da biste uploadovali sliku');
      return;
    }

    try {
      setUploading(true);
      await dogsAPI.uploadImage(id, file);
      setSuccess('Slika uspešno uploadovana');
      fetchImages();
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška pri uploadu slike');
    } finally {
      setUploading(false);
    }
  };

  const handlePickedUp = async () => {
    if (!user) {
      setError('Morate biti prijavljeni');
      return;
    }

    if (!window.confirm('Da li ste sigurni da ste spasili ovog psa?')) {
      return;
    }

    try {
      await dogsAPI.markPickedUp(id);
      setSuccess('Pas označen kao spašen. Čeka potvrdu administratora.');
      fetchDog();
      setTimeout(() => setSuccess(''), 5000);
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška');
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

  if (!dog) {
    return <div className="container"><div className="alert alert-error">Pas nije pronađen</div></div>;
  }

  return (
    <div className="container">
      <div className="card">
        <Link to="/dogs" style={{ marginBottom: '20px', display: 'inline-block' }}>
          ← Nazad na listu
        </Link>

        <h2>{dog.title}</h2>
        <span className={`status-badge status-${dog.status}`}>
          {getStatusLabel(dog.status)}
        </span>

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <div style={{ marginTop: '20px' }}>
          <h3>Opis</h3>
          <p>{dog.description || 'Nema opisa'}</p>
        </div>

        <div style={{ marginTop: '20px' }}>
          <h3>Lokacija</h3>
          <p>📍 {dog.latitude}, {dog.longitude}</p>
        </div>

        {dog.reporter && (
          <div style={{ marginTop: '20px' }}>
            <h3>Prijavio</h3>
            <p>{dog.reporter.full_name}</p>
          </div>
        )}

        {dog.picked_up_by && (
          <div style={{ marginTop: '20px' }}>
            <h3>Spašio</h3>
            <p>{dog.picked_up_by.full_name}</p>
          </div>
        )}

        <div style={{ marginTop: '30px' }}>
          <h3>Fotografije</h3>
          {images.length > 0 ? (
            <div className="image-grid">
              {images.map((image) => 
                image && image.url ? (
                  <img
                    key={image.id}
                    src={image.url.startsWith('http') ? image.url : `http://localhost:8000${image.url}`}
                    alt={dog.title}
                  />
                ) : null
              )}
            </div>
          ) : (
            <p>Nema fotografija</p>
          )}

          {user && (
            <div style={{ marginTop: '20px' }}>
              <label className="btn btn-secondary" style={{ cursor: 'pointer' }}>
                {uploading ? 'Upload...' : 'Dodaj fotografiju'}
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleFileUpload}
                  style={{ display: 'none' }}
                  disabled={uploading}
                />
              </label>
            </div>
          )}
        </div>

        {user && dog.status === 'reported' && (
          <div style={{ marginTop: '30px' }}>
            <button onClick={handlePickedUp} className="btn btn-success">
              Označi kao spašenog
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default DogDetail;
