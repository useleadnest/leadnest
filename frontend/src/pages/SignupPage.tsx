import React from 'react';
import { useNavigate } from 'react-router-dom';
import RegisterForm from '../components/RegisterForm';

const SignupPage: React.FC = () => {
  const navigate = useNavigate();
  
  return <RegisterForm onToggle={() => navigate('/login')} />;
};

export default SignupPage;
