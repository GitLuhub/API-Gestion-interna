import { apiSlice } from '../../store/apiSlice';

export const rolesApi = apiSlice.injectEndpoints({
  endpoints: (builder) => ({
    getRoles: builder.query({
      query: () => '/roles/',
      providesTags: (result = []) => [
        'Role',
        ...result.map(({ id }: { id: string }) => ({ type: 'Role' as const, id })),
      ],
    }),
    createRole: builder.mutation({
      query: (role) => ({
        url: '/roles/',
        method: 'POST',
        body: role,
      }),
      invalidatesTags: ['Role'],
    }),
    assignRole: builder.mutation({
      query: ({ roleId, userId }) => ({
        url: `/roles/${roleId}/assign/${userId}`,
        method: 'POST',
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'User', id: userId }
      ],
      // Since assign/revoke role doesn't return the full updated user object, we just invalidate the specific user or all users to trigger a refetch.
      // Wait, we can optionally optimistically update the User cache if we know the role object, but invalidation is safer for nested objects.
    }),
    revokeRole: builder.mutation({
      query: ({ roleId, userId }) => ({
        url: `/roles/${roleId}/revoke/${userId}`,
        method: 'DELETE',
      }),
      invalidatesTags: (result, error, { userId }) => [
        { type: 'User', id: userId }
      ],
    }),
  }),
});

export const {
  useGetRolesQuery,
  useCreateRoleMutation,
  useAssignRoleMutation,
  useRevokeRoleMutation,
} = rolesApi;
