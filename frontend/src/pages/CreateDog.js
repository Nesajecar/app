import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { dogsAPI } from '../services/api';

const CreateDog = () => {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const data = {
        title,
        description,
        latitude: parseFloat(latitude),
        longitude: parseFloat(longitude),
      };

      const response = await dogsAPI.create(data);
      navigate(`/dogs/${response.data.id}`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Greška pri kreiranju prijave');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = () => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLatitude(position.coords.latitude.toFixed(6));
          setLongitude(position.coords.longitude.toFixed(6));
        },
        (error) => {
          setError('Greška pri dobijanju lokacije');
        }
      );
    } else {
      setError('Geolokacija nije podržana u vašem browseru');
    }
  };

  return (
    <div className="container">
      <div className="card" style={{ maxWidth: '600px', margin: '20px auto' }}>
        <h2>Prijavi novog psa</h2>

        {error && <div className="alert alert-error">{error}</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>Naziv / Kratak opis *</label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
              placeholder="npr. Pas na ulici u centru"
            />
          </div>

          <div className="form-group">
            <label>Detaljan opis</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Opis psa, boja, veličina, itd."
            />
          </div>

          <div className="form-group">
            <label>Geolokacija *</label>
            <button
              type="button"
              onClick={getCurrentLocation}
              className="btn btn-secondary btn-small"
              style={{ marginBottom: '10px' }}
            >
              Koristi trenutnu lokaciju
            </button>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '10px' }}>
              <div>
                <label style={{ fontSize: '14px' }}>Latitude</label>
                <input
                  type="number"
                  step="any"
                  value={latitude}
                  onChange={(e) => setLatitude(e.target.value)}
                  required
                  placeholder="44.7866"
                  min="-90"
                  max="90"
                />
              </div>
              <div>
                <label style={{ fontSize: '14px' }}>Longitude</label>
                <input
                  type="number"
                  step="any"
                  value={longitude}
                  onChange={(e) => setLongitude(e.target.value)}
                  required
                  placeholder="20.4489"
                  min="-180"
                  max="180"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary"
            style={{ width: '100%' }}
            disabled={loading}
          >
            {loading ? 'Kreiranje...' : 'Prijavi psa'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default CreateDog;
