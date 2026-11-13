import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class UserManagementService {
  private usersQuery = gql`
    query GetUsers {
      users(orderBy: "createdAt_DESC", limit: 100) {
        id
        username
        email
        fullName
        role
        isActive
        lastLogin
        createdAt
      }
    }
  `;

  constructor(private apollo: Apollo) {}

  getUsers() {
    return this.apollo.watchQuery({
      query: this.usersQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.users || [])
    );
  }
}
