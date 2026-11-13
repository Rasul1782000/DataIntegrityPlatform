import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

import { LogSource } from '../../shared/models/log-source.model';
import { SecurityEvent } from '../../shared/models/log-event.model';

/**
 * Fields must match the log source model and the LogMonitoringComponent
 * template: sourceName, sourceType, sourcePath, healthStatus, lastReadAt.
 */
const LOG_SOURCES_QUERY = gql`
  query GetLogSources {
    logSources(orderBy: "createdAt_DESC", limit: 50) {
      id
      sourceName
      sourceType
      sourcePath
      healthStatus
      lastReadAt
    }
  }
`;

/**
 * Fields must match the SecurityEvent model and the live log viewer:
 * eventCategory, severity, eventDescription, normalizedTimestamp, status.
 */
const SECURITY_EVENTS_QUERY = gql`
  query GetSecurityEvents {
    securityEvents(orderBy: "normalizedTimestamp_DESC", limit: 100) {
      id
      eventCategory
      severity
      eventDescription
      normalizedTimestamp
      status
    }
  }
`;

@Injectable({ providedIn: 'root' })
export class LogMonitoringService {
  constructor(private apollo: Apollo) {}

  getLogSources() {
    return this.apollo.watchQuery({
      query: LOG_SOURCES_QUERY,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.logSources || [] as LogSource[])
    );
  }

  getSecurityEvents(): any {
    return this.apollo.watchQuery({
      query: SECURITY_EVENTS_QUERY,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.securityEvents || [] as SecurityEvent[])
    );
  }

  getRecentEvents() {
    return this.getSecurityEvents();
  }
}
