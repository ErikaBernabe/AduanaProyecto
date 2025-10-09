import './LoginScreen.css';
import { useForm }  from 'react-hook-form';

const LoginScreen = ({ onLoginSuccess }) => {
  const { register, handleSubmit } = useForm();
  const onSubmit = (data) => {
  console.log(data);
  onLoginSuccess();
  }
    return (
      <form className='Login' onSubmit={handleSubmit(onSubmit)}>
        <h2>Crucero Fronterizo</h2>

        <input placeholder="Ingrese su Email" {...register("usuario")}></input>

        <input placeholder="Ingrese su contraseña" {...register("contraseña")}></input>

        <button type='submit'>Ingresar</button>
      </form>
  );
}

export default LoginScreen;
