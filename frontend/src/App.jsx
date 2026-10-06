import { Route, Routes } from 'react-router-dom';
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import ProtectedRoute from './components/ProtectedRoute';
import DashboardPage from './pages/DashboardPage';


const Stub = ({ name }) => <div className='p-10 text-xl'>{name} (komt later)</div>;

function App() {
  return (
    <Routes>
      <Route path='/' element={<HomePage />} />
      <Route path='/register?mode=login' element={<Stub name="Inloggen" />} />
      <Route path='/register' element={< AuthPage />} />
      <Route path="/app" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
    </Routes>
  );
}

export default App;
