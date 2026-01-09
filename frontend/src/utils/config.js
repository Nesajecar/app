// Helper funkcija za dobijanje base URL-a za slike
export const getImageUrl = (imagePath) => {
  // Ako je već pun URL, vrati ga
  if (imagePath.startsWith('http')) {
    return imagePath;
  }
  // Inače dodaj base URL
  return `http://localhost:8000${imagePath}`;
};

// API base URL
export const API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
