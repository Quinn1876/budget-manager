"use client";

import { HttpLink, ApolloLink } from "@apollo/client";
import { ApolloClient, InMemoryCache, ApolloNextAppProvider, SSRMultipartLink   } from "@apollo/client-integration-nextjs";

function makeClient() {
  const httpLink = new HttpLink({
      uri: "http://localhost:5000/graphql",
  });

  return new ApolloClient({
    cache: new InMemoryCache(),
    link:
      typeof window === "undefined"
        ? ApolloLink.from([
            new SSRMultipartLink({
              stripDefer: true,
            }),
            httpLink,
          ])
        : httpLink,
  });
}

export function ApolloProvider({ children }: React.PropsWithChildren) {
  return (
    <ApolloNextAppProvider makeClient={makeClient}>
      {children}
    </ApolloNextAppProvider>
  );
}
