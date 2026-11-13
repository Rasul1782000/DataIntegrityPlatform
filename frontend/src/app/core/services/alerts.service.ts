import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AlertsService {
  private alertsQuery = gql`
    query GetAlerts {
      alerts(orderBy: "createdAt_DESC", limit: 50) {
        id
        alertType
        title
        description
        severity
        status
        assignedTo
        deduplicationKey
        createdAt
        resolvedAt
      }
    }
  `;

  constructor(private apollo: Apollo) {}

  getAlerts() {
    return this.apollo.watchQuery({
      query: this.alertsQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.alerts || [])
    );
  }

  acknowledgeAlert(alertId: string) {
    // TODO: Implement acknowledge alert mutation
  }

  resolveAlert(alertId: string, notes?: string) {
    // TODO: Implement resolve alert mutation
  }

  assignAlert(alertId: string, userId: string) {
    // TODO: Implement assign alert mutation
  }
}
