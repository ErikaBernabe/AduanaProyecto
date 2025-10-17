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
    <div className='Login'>
      <img src="/frontera.png" alt="Logo EFrontera" className="login-logo" />
      <form className='login-form' onSubmit={handleSubmit(onSubmit)}>
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
