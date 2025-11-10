import React from 'react';
import { useForm } from 'react-hook-form';
import { useToast } from '../hooks/useToast';
import '../styles/LoginScreen.css';

const LoginScreen = ({ onLoginSuccess }) => {
  const { register, handleSubmit } = useForm();
  const toast = useToast();

  const onSubmit = (data) => {
    if (data.usuario === "eFrontera@gmail.com" && data.contraseña === "1234") {
      onLoginSuccess();
    } else {
      toast.error("❌ Credenciales inválidas");
    }
  };

  return (
    <div className='Login'>
      <form className='login-form' onSubmit={handleSubmit(onSubmit)}>
        <img src="/frontera.png" alt="Logo EFrontera" className="login-logo" />
        <h2>Crucero Fronterizo</h2>

        <input
          placeholder="Ingrese su Email"
          type="email"
          {...register("usuario")}
        />

        <input
          placeholder="Ingrese su contraseña"
          type="password"
          {...register("contraseña")}
        />

        <button type='submit'>Ingresar</button>
      </form>
    </div>
  );
};

export default LoginScreen;
