import { Routes } from '@angular/router';
import { DashboardComponent } from './core/pages/dashboard/dashboard.component';
import { FileIntegrityComponent } from './core/pages/file-integrity/file-integrity.component';
import { LogMonitoringComponent } from './core/pages/log-monitoring/log-monitoring.component';
import { ThreatDetectionComponent } from './core/pages/threat-detection/threat-detection.component';
import { AlertsComponent } from './core/pages/alerts/alerts.component';
import { AuditComponent } from './core/pages/audit/audit.component';
import { ReportsComponent } from './core/pages/reports/reports.component';
import { UserManagementComponent } from './core/pages/user-management/user-management.component';

export const appRoutes: Routes = [
  {
    path: 'dashboard',
    component: DashboardComponent,
  },
  {
    path: 'file-integrity',
    component: FileIntegrityComponent,
  },
  {
    path: 'log-monitoring',
    component: LogMonitoringComponent,
  },
  {
    path: 'threat-detection',
    component: ThreatDetectionComponent,
  },
  {
    path: 'alerts',
    component: AlertsComponent,
  },
  {
    path: 'audit',
    component: AuditComponent,
  },
  {
    path: 'reports',
    component: ReportsComponent,
  },
  {
    path: 'user-management',
    component: UserManagementComponent,
  },
  {
    path: '',
    redirectTo: 'dashboard',
    pathMatch: 'full',
  },
  {
    path: '**',
    redirectTo: 'dashboard',
  },
];
