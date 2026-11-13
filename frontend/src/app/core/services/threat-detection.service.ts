import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

/**
 * Fields must match the DetectionRule model and the ThreatDetectionComponent
 * template: ruleName, ruleType, severity, threshold, enabled.
 */
const DETECTION_RULES_QUERY = gql`
  query GetDetectionRules {
    detectionRules(orderBy: "createdAt_DESC", limit: 50) {
      id
      ruleName
      ruleType
      severity
      threshold
      enabled
    }
  }
`;

/**
 * Fields must match the Threat model (suspicious IP summary) and the
 * template: sourceIp, associatedUsernames, firstSeenAt, lastSeenAt,
 * failedAuthentications, severity.
 */
const SUSPICIOUS_IPS_QUERY = gql`
  query GetSuspiciousIPs {
    suspiciousIPs(orderBy: "lastSeenAt_DESC", limit: 100) {
      sourceIp
      associatedUsernames
      firstSeenAt
      lastSeenAt
      failedAuthentications
      severity
    }
  }
`;

@Injectable({ providedIn: 'root' })
export class ThreatDetectionService {
  constructor(private apollo: Apollo) {}

  getDetectionRules() {
    return this.apollo.watchQuery({
      query: DETECTION_RULES_QUERY,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.detectionRules || [])
    );
  }

  getSuspiciousIPs() {
    return this.apollo.watchQuery({
      query: SUSPICIOUS_IPS_QUERY,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.suspiciousIPs || [])
    );
  }
}
