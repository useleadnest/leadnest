import { Navigate } from 'react-router-dom';

export default function ProtectedRoute({ children }: { children: JSX.Element }) {
  const token = localStorage.getItem('ln_token');
  return token ? children : <Navigate to="/login" replace />;
}
