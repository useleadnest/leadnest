import React, { createContext, useContext, useEffect, useState } from 'react';
import { Auth } from '../lib/api';

interface AuthUser {
  email: string;
  sub?: string;
}

type AuthCtx = {
  user: AuthUser | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  loading: boolean;
};

// Simple JWT decoder (for payload extraction)
const decodeToken = (token: string): AuthUser | null => {
  try {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    const payload = JSON.parse(jsonPayload);
    return {
      email: payload.email || payload.sub,
      sub: payload.sub,
    };
  } catch (error) {
    console.error('Error decoding token:', error);
    return null;
  }
};

const AuthContext = createContext<AuthCtx | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const storedToken = localStorage.getItem('ln_token');
    if (storedToken) {
      const decoded = decodeToken(storedToken);
      if (decoded) {
        setToken(storedToken);
        setUser(decoded);
      } else {
        localStorage.removeItem('ln_token');
      }
    }
    setLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await Auth.login(email, password);
    const decoded = decodeToken(response.token);
    
    if (decoded) {
      localStorage.setItem('ln_token', response.token);
      setToken(response.token);
      setUser(decoded);
    } else {
      throw new Error('Invalid token received');
    }
  };

  const register = async (email: string, password: string) => {
    const response = await Auth.register(email, password);
    const decoded = decodeToken(response.token);
    
    if (decoded) {
      localStorage.setItem('ln_token', response.token);
      setToken(response.token);
      setUser(decoded);
    } else {
      throw new Error('Invalid token received');
    }
  };

  const logout = () => {
    localStorage.removeItem('ln_token');
    setToken(null);
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
