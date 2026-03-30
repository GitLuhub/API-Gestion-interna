import React from 'react';
import { useGetRolesQuery } from './rolesApi';

export const RolesList = () => {
  const { data: roles, isLoading, isError } = useGetRolesQuery({});

  if (isLoading) return <div>Cargando roles...</div>;
  if (isError) return <div>Error al cargar roles</div>;

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold mb-4 text-gray-800">Roles del Sistema</h2>
      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {roles?.map((role: any) => (
            <li key={role.id}>
              <div className="px-4 py-4 sm:px-6">
                <div className="flex items-center justify-between">
                  <p className="text-sm font-medium text-purple-600 truncate">{role.name}</p>
                </div>
                <div className="mt-2 sm:flex sm:justify-between">
                  <div className="sm:flex">
                    <p className="flex items-center text-sm text-gray-500">
                      {role.description || 'Sin descripción'}
                    </p>
                  </div>
                </div>
              </div>
            </li>
          ))}
          {(!roles || roles.length === 0) && (
            <li className="px-4 py-4 sm:px-6 text-gray-500 text-center">No hay roles registrados</li>
          )}
        </ul>
      </div>
    </div>
  );
};
