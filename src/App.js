import { useState } from 'react';
import './styles/App.css';
import LoginScreen from './pages/LoginScreen';
import InspectionScreen from './pages/InspectionScreen';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  const handleLogin = () => {
    setIsLoggedIn(true);
  };

  return (
    <>
      {isLoggedIn ? (
        <InspectionScreen />
      ) : (
        <LoginScreen onLoginSuccess={handleLogin} />
      )}
    </>
  );
}

export default App;
