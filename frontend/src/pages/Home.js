import React from 'react';
import { Link } from 'react-router-dom';
import { useContext } from 'react';
import { AuthContext } from '../context/AuthContext';

const Home = () => {
  const { user } = useContext(AuthContext);

  return (
    <div className="container">
      <div className="card">
        <h1>🐕 Dobrodošli u Dog Rescue</h1>
        <p style={{ fontSize: '18px', marginBottom: '20px' }}>
          Sistem za prijavu izgubljenih i nađenih pasa sa potvrdom spašavanja
        </p>

        <div style={{ marginTop: '30px' }}>
          <h2>Kako funkcioniše?</h2>
          <ol style={{ marginLeft: '20px', marginTop: '15px', lineHeight: '1.8' }}>
            <li>Prijavi psa koji je viđen na ulici</li>
            <li>Dodaj fotografije i lokaciju</li>
            <li>Drugi korisnici mogu prijaviti da su psa spasili</li>
            <li>Administrator potvrđuje spašavanje</li>
          </ol>
        </div>

        <div style={{ marginTop: '30px', display: 'flex', gap: '15px', flexWrap: 'wrap' }}>
          <Link to="/dogs" className="btn btn-primary">
            Pregledaj prijavljene pse
          </Link>
          {user ? (
            <Link to="/dogs/create" className="btn btn-success">
              Prijavi novog psa
            </Link>
          ) : (
            <Link to="/signup" className="btn btn-success">
              Registruj se
            </Link>
          )}
        </div>
      </div>
    </div>
  );
};

export default Home;
