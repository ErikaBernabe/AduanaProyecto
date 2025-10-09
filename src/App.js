import logo from './logo.svg';
import './App.css';
import LoginScreen from "./LoginScreen";
import InspectionScreen from './InspectionScreen';
import { useState } from 'react';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const handleLogin = () => {
    setIsLoggedIn(true)
  }
  return (
    isLoggedIn ? <InspectionScreen></InspectionScreen> : <LoginScreen onLoginSuccess = {handleLogin}></LoginScreen>
  );
}

export default App;
