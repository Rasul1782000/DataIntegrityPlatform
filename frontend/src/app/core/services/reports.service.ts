import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

/**
 * Fields must match the Report model and the ReportsComponent template:
 * title, type, generatedAt, recordCount.
 */
const REPORTS_QUERY = gql`
  query GetReports {
    reports(orderBy: "generatedAt_DESC", limit: 50) {
      id
      title
      type
      generatedAt
      recordCount
      format
    }
  }
`;

@Injectable({ providedIn: 'root' })
export class ReportsService {
  constructor(private apollo: Apollo) {}

  getReports() {
    return this.apollo.watchQuery({
      query: REPORTS_QUERY,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.reports || [])
    );
  }
}
