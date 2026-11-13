import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class DashboardService {
  private dashboardQuery = gql`
    query GetDashboardSummary {
      dashboardSummary {
        totalMonitoredDirectories
        totalMonitoredFiles
        modifiedFilesToday
        addedFilesToday
        deletedFilesToday
        totalLogEvents
        failedLoginAttempts
        activeThreats
        criticalAlerts
        lastSuccessfulScan
      }
    }
  `;

  constructor(private apollo: Apollo) {}

  getDashboardSummary() {
    return this.apollo.watchQuery({
      query: this.dashboardQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.dashboardSummary)
    );
  }
}
