import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';
import { BehaviorSubject, Observable } from 'rxjs';

import { User } from '../../shared/models/user.model';

/**
 * GraphQL operations — must match the Strawberry schema exposed by the
 * Python backend at /graphql (app/schema.py, app/modules/auth/graphql).
 */
const LOGIN_MUTATION = gql`
  mutation Login($input: LoginInput!) {
    login(input: $input) {
      accessToken
      refreshToken
      tokenType
      expiresIn
      user {
        id
        username
        email
        role
        isActive
        createdAt
        lastLogin
        isLocked
        isMfaEnabled
      }
      rememberMe
      mfaVerified
    }
  }
`;

const ME_QUERY = gql`
  query Me {
    me {
      id
      username
      email
      role
      isActive
      createdAt
      lastLogin
      isLocked
      isMfaEnabled
    }
  }
`;

const REFRESH_SESSION_MUTATION = gql`
  mutation RefreshSession($refreshToken: String!) {
    refreshSession(refreshToken: $refreshToken) {
      accessToken
      refreshToken
      tokenType
      expiresIn
      user {
        id
        username
        email
        role
        isActive
        createdAt
        lastLogin
        isLocked
        isMfaEnabled
      }
      rememberMe
      mfaVerified
    }
  }
`;

const LOGOUT_MUTATION = gql`
  mutation Logout($refreshToken: String!) {
    logout(refreshToken: $refreshToken)
  }
`;

const ACCESS_TOKEN_KEY = 'access_token';
const REFRESH_TOKEN_KEY = 'refresh_token';
const CURRENT_USER_KEY = 'currentUser';

@Injectable({ providedIn: 'root' })
export class AuthService {
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public user$ = this.currentUserSubject.asObservable();

  constructor(private apollo: Apollo) {
    this.initializeUser();
  }

  private initializeUser() {
    const storedUser = localStorage.getItem(CURRENT_USER_KEY);
    if (storedUser) {
      this.currentUserSubject.next(JSON.parse(storedUser));
    }
    // Re-validate the stored token against the backend (`me` query).
    this.loadCurrentUser().subscribe();
  }

  public get userValue(): User | null {
    return this.currentUserSubject.value;
  }

  public get accessToken(): string | null {
    return localStorage.getItem(ACCESS_TOKEN_KEY);
  }

  /**
   * Backend operation: `login(input: LoginInput!)` -> AuthPayload
   */
  login(username: string, password: string, rememberMe = false, mfaCode?: string): Observable<User | null> {
    return this.apollo.mutate({
      mutation: LOGIN_MUTATION,
      variables: { input: { username, password, rememberMe, mfaCode } },
    }).pipe(
      map((result: any) => {
        const payload = result?.data?.login;
        if (!payload) {
          return null;
        }
        this.setSession(payload.accessToken, payload.refreshToken, payload.user);
        return payload.user;
      })
    );
  }

  /**
   * Backend operation: `me` -> UserType | null.
   * Refreshes the locally stored user from the backend.
   */
  loadCurrentUser(): Observable<User | null> {
    return this.apollo.query({
      query: ME_QUERY,
      fetchPolicy: 'network-only',
    }).pipe(
      map((result: any) => {
        const user = result?.data?.me;
        if (user) {
          this.currentUserSubject.next(user);
          localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
        } else {
          this.clearSession();
        }
        return user;
      })
    );
  }

  /**
   * Backend operation: `refreshSession(refreshToken: String!)` -> AuthPayload
   */
  refreshSession(): Observable<User | null> {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    return this.apollo.mutate({
      mutation: REFRESH_SESSION_MUTATION,
      variables: { refreshToken },
    }).pipe(
      map((result: any) => {
        const payload = result?.data?.refreshSession;
        if (!payload) {
          return null;
        }
        this.setSession(payload.accessToken, payload.refreshToken, payload.user);
        return payload.user;
      })
    );
  }

  /**
   * Backend operation: `logout(refreshToken: String!)` -> Boolean
   */
  logout(): void {
    const refreshToken = localStorage.getItem(REFRESH_TOKEN_KEY);
    if (refreshToken) {
      // Best-effort revoke on the backend; local session is cleared regardless.
      this.apollo.mutate({
        mutation: LOGOUT_MUTATION,
        variables: { refreshToken },
      }).subscribe({ error: () => undefined });
    }
    this.clearSession();
  }

  private setSession(accessToken: string, refreshToken: string, user: User): void {
    localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
    localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
    localStorage.setItem(CURRENT_USER_KEY, JSON.stringify(user));
    this.currentUserSubject.next(user);
  }

  private clearSession(): void {
    localStorage.removeItem(ACCESS_TOKEN_KEY);
    localStorage.removeItem(REFRESH_TOKEN_KEY);
    localStorage.removeItem(CURRENT_USER_KEY);
    this.currentUserSubject.next(null);
  }
}
