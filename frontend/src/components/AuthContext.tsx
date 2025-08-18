import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User } from '../types';
import { authAPI } from '../services/api';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, businessName?: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('ln_token');
    if (token) {
      // Try to decode user info from token
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const now = Date.now() / 1000;
        
        if (payload.exp && payload.exp > now) {
          setUser({
            id: payload.user_id,
            email: payload.sub,
            business_id: payload.business_id,
          });
        } else {
          localStorage.removeItem('ln_token');
        }
      } catch (error) {
        localStorage.removeItem('ln_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await authAPI.login(email, password);
    localStorage.setItem('ln_token', response.token);
    setUser(response.user);
  };

  const register = async (email: string, password: string, businessName?: string) => {
    const response = await authAPI.register(email, password, businessName || '');
    localStorage.setItem('ln_token', response.token);
    setUser(response.user);
  };

  const logout = () => {
    localStorage.removeItem('ln_token');
    setUser(null);
  };

  const value = {
    user,
    login,
    register,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
