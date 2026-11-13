import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class AuditService {
  private auditLogsQuery = gql`
    query GetAuditLogs {
      auditLogs(orderBy: "timestamp_DESC", limit: 100) {
        id
        actorId
        actorUsername
        action
        entityType
        entityId
        previousValue
        newValue
        note
        timestamp
        previousRecordHash
        recordHash
      }
    }
  `;

  constructor(private apollo: Apollo) {}

  getAuditLogs() {
    return this.apollo.watchQuery({
      query: this.auditLogsQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.auditLogs || [])
    );
  }

  getRecordHash(logId: string) {
    // TODO: Implement get specific record hash query
    return null;
  }

  verifyChain() {
    // TODO: Implement chain verification
    return true;
  }
}
