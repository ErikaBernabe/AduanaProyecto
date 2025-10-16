import React from 'react';
import { useForm } from 'react-hook-form';
import '../styles/LoginScreen.css';

const LoginScreen = ({ onLoginSuccess }) => {
  const { register, handleSubmit } = useForm();

  const onSubmit = (data) => {
    console.log(data);
    onLoginSuccess();
  };

  return (
    <form className='Login' onSubmit={handleSubmit(onSubmit)}>
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
  );
};

export default LoginScreen;
