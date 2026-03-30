import React from 'react';
import { render, screen, fireEvent, waitFor } from '../../test-utils';
import userEvent from '@testing-library/user-event';
import Login from './Login';
import { server } from '../../mocks/server';
import { http, HttpResponse } from 'msw';

describe('Login Component', () => {
  test('renders login form', () => {
    render(<Login />);
    
    expect(screen.getByText(/Iniciar Sesión/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Contraseña/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Entrar/i })).toBeInTheDocument();
  });

  test('shows error message on invalid credentials', async () => {
    render(<Login />);
    const user = userEvent.setup();

    await user.type(screen.getByLabelText(/Email/i), 'wrong@example.com');
    await user.type(screen.getByLabelText(/Contraseña/i), 'wrongpass');
    
    await user.click(screen.getByRole('button', { name: /Entrar/i }));

    expect(await screen.findByText(/Error al iniciar sesión/i)).toBeInTheDocument();
  });

  test('successful login redirects or updates state', async () => {
    render(<Login />);
    const user = userEvent.setup();

    await user.type(screen.getByLabelText(/Email/i), 'admin@example.com');
    await user.type(screen.getByLabelText(/Contraseña/i), 'admin123');
    
    await user.click(screen.getByRole('button', { name: /Entrar/i }));

    await waitFor(() => {
      expect(screen.queryByText(/Entrando/i)).not.toBeInTheDocument();
    });
    
    expect(screen.queryByText(/Error al iniciar sesión/i)).not.toBeInTheDocument();
  });
});
