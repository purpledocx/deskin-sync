import { useEffect, useState } from 'react';
import { getHealth } from '../api/client';

function HomePage() {
  const [apiStatus, setApiStatus] = useState('Cheking API...');

  useEffect(() => {
    getHealth()
      .then((data) => setApiStatus(`API status: ${data.status}`))
      .catch(() => setApiStatus('API is unavailable'));
  }, []);

  return (
    <main>
      <h1>DeskIn Sync</h1>
      <p>Book workspaces and meeting rooms.</p>
      <p>{apiStatus}</p>
    </main>
  );
}

export default HomePage;
