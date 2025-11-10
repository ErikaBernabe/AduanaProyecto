import { useState } from 'react';
import './styles/App.css';
import LoginScreen from './pages/LoginScreen';
import InspectionScreen from './pages/InspectionScreen';
import { ToastProvider } from './contexts/ToastContext';
import ToastContainer from './components/Toast/ToastContainer';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
  };

  return (
    <ToastProvider>
      <ToastContainer />
      {isLoggedIn ? (
        <InspectionScreen onLogout={handleLogout} />
      ) : (
        <LoginScreen onLoginSuccess={handleLogin} />
      )}
    </ToastProvider>
  );
}

export default App;
