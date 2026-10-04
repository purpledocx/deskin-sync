import { Route, Routes } from 'react-router-dom';
import LandingPage from './pages/LandingPage';


const Stub = ({ name }) => <div className='p-10 text-xl'>{name} (komt later)</div>;

function App() {
  return (
    <Routes>
      <Route path='/' element={<LandingPage />} />
      <Route path='/register?mode=login' element={<Stub name="Inloggen" />} />
      <Route path='/register' element={<Stub name="Register" />} />
      <Route path='/dashboard' element={<Stub name="Dashboard" />} />
    </Routes>
  );
}

export default App;
