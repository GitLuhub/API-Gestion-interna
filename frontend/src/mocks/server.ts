import { setupServer } from 'msw/node';
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.post('http://localhost:8000/api/v1/auth/login', async ({ request }) => {
    const data = await request.json() as { email?: string; password?: string };
    
    if (data.email === 'admin@example.com' && data.password === 'admin123') {
      return HttpResponse.json({
        access_token: 'mock-access-token',
        token_type: 'bearer',
      });
    }
    
    return HttpResponse.json(
      { detail: 'Email o contraseña incorrectos' },
      { status: 401 }
    );
  }),

  http.get('http://localhost:8000/api/v1/users/', () => {
    return HttpResponse.json([
      { id: '1', email: 'admin@example.com', first_name: 'Admin', last_name: 'User', is_active: true },
      { id: '2', email: 'user@example.com', first_name: 'Test', last_name: 'User', is_active: true }
    ]);
  }),
];

export const server = setupServer(...handlers);