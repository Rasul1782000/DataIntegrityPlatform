export interface DashboardSummary {
  totalMonitoredDirectories: number;
  totalMonitoredFiles: number;
  modifiedFilesToday: number;
  addedFilesToday: number;
  deletedFilesToday: number;
  totalLogEvents: number;
  failedLoginAttempts: number;
  activeThreats: number;
  criticalAlerts: number;
  lastSuccessfulScan?: Date;
}