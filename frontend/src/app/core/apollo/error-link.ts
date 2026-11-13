import { onError } from '@apollo/client/link/error';

/**
 * Centralized GraphQL error handling link.
 * Logs GraphQL and network errors; extend here for user-facing
 * error notifications or global session-expiry handling.
 */
export const errorLink = onError(({ graphQLErrors, networkError }) => {
  if (graphQLErrors) {
    graphQLErrors.forEach(({ message, locations, path }) => {
      console.error(
        `[GraphQL error]: Message: ${message}, Location: ${JSON.stringify(locations)}, Path: ${path}`
      );
    });
  }
  if (networkError) {
    console.error(`[Network error]: ${networkError}`);
  }
});
