import { APOLLO_OPTIONS } from 'apollo-angular';
import { HttpLink } from 'apollo-angular/http';
import { ApolloClient, ApolloLink, InMemoryCache } from '@apollo/client';
import { setContext } from '@apollo/client/link/context';
import { environment } from '../../../environments/environment';
import { errorLink } from './error-link';

export function createApollo(httpLink: HttpLink): ApolloClient<any> {
  const authLink = setContext((request, previousContext) => {
    const token = localStorage.getItem('access_token');
    return {
      headers: {
        Authorization: token ? `Bearer ${token}` : '',
      },
    };
  });

  const http = httpLink.create({ uri: environment.graphqlUrl });

  return new ApolloClient({
    link: ApolloLink.from([errorLink, authLink, http]),
    cache: new InMemoryCache(),
    defaultOptions: {
      watchQuery: {
        fetchPolicy: 'cache-and-network',
        errorPolicy: 'none',
      },
      query: {
        fetchPolicy: 'cache-first',
        errorPolicy: 'none',
      },
      mutate: {
        fetchPolicy: 'no-cache',
        errorPolicy: 'none',
      },
    },
  });
}

export const apolloProviders = [
  {
    provide: APOLLO_OPTIONS,
    useFactory: createApollo,
    deps: [HttpLink],
  },
];
