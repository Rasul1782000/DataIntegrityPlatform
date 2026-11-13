import { Injectable } from '@angular/core';
import { Apollo, gql } from 'apollo-angular';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class FileIntegrityService {
  private directoriesQuery = gql`
    query GetMonitoredDirectories {
      monitoredDirectories {
        id
        name
        canonicalPath
        monitoringEnabled
        scanFrequency
      }
    }
  `;

  private eventsQuery = gql`
    query GetRecentFileEvents {
      fileIntegrityEvents(orderBy: "detectedAt_DESC", limit: 20) {
        id
        directoryName
        relativePath
        eventType
        previousHash
        currentHash
        severity
        detectedAt
        status
      }
    }
  `;

  private baselinesQuery = gql`
    query GetBaselinesCount {
      fileBaselinesAggregate {
        count
      }
    }
  `;

  constructor(private apollo: Apollo) {}

  getMonitoredDirectories() {
    return this.apollo.watchQuery({
      query: this.directoriesQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.monitoredDirectories || [])
    );
  }

  getRecentEvents() {
    return this.apollo.watchQuery({
      query: this.eventsQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.fileIntegrityEvents || [])
    );
  }

  getBaselinesCount() {
    return this.apollo.watchQuery({
      query: this.baselinesQuery,
      fetchPolicy: 'cache-and-network',
    }).valueChanges.pipe(
      map((result: any) => result.data?.fileBaselinesAggregate?.count || 0)
    );
  }

  registerDirectory(directoryData: any) {
    // TODO: Implement directory registration mutation
  }

  startScan(directoryId: string) {
    // TODO: Implement start scan mutation
  }
}
