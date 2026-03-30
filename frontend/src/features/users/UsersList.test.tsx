import React from 'react';
import { render, screen, waitFor } from '../../test-utils';
import UsersList from './UsersList';

describe('UsersList Component', () => {
  test('renders users loading state and then data', async () => {
    render(<UsersList />);

    expect(screen.getByText(/Cargando/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.queryByText(/Cargando/i)).not.toBeInTheDocument();
    });

    expect(await screen.findByText('admin@example.com')).toBeInTheDocument();
    expect(screen.getByText('user@example.com')).toBeInTheDocument();
  });
});
