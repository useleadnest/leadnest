import React, { createContext, useContext, useEffect, useState } from 'react';
import { api } from '../lib/api';

type User = { email: string } | null;

type AuthCtx = {
  user: User;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthCtx | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [token, setToken] = useState<string | null>(() => localStorage.getItem('ln_token'));
  const [user, setUser] = useState<User>(() => {
    const email = localStorage.getItem('ln_email');
    return email ? { email } : null;
  });

  useEffect(() => {
    if (token) localStorage.setItem('ln_token', token);
    else localStorage.removeItem('ln_token');
  }, [token]);

  const login = async (email: string, password: string) => {
    const res = await api<{ token: string }>(`/auth/login`, {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    setToken(res.token);
    setUser({ email });
    localStorage.setItem('ln_email', email);
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('ln_email');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
};
