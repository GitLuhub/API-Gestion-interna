import React from 'react';
import { useGetUsersQuery } from './usersApi';

export const UsersList = () => {
  const { data: users, isLoading, isError } = useGetUsersQuery({});

  if (isLoading) return <div>Cargando usuarios...</div>;
  if (isError) return <div>Error al cargar usuarios</div>;

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">Usuarios</h2>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {users?.map((user: any) => (
            <li key={user.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-blue-600 truncate">{user.first_name} {user.last_name}</p>
                  <div className="ml-2 flex-shrink-0 flex">
                    <p className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
                      {user.is_active ? 'Activo' : 'Inactivo'}
                    </p>
                  </div>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      {user.email}
                    </p>
                  </div>
                </div>
              </div>
            </li>
          ))}
          {(!users || users.length === 0) && (
            <li className="px-4 py-4 sm:px-6 text-gray-500 text-center">No hay usuarios registrados</li>
          )}
        </ul>
      </div>
    </div>
  );
};
