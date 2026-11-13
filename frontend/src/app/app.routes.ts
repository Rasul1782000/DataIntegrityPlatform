import { Routes } from '@angular/router';
import { AuthGuard } from './core/authentication/guards/auth.guard';

import { DashboardComponent } from './core/pages/dashboard/dashboard.component';
import { FileIntegrityComponent } from './core/pages/file-integrity/file-integrity.component';
import { LogMonitoringComponent } from './core/pages/log-monitoring/log-monitoring.component';
import { ThreatDetectionComponent } from './core/pages/threat-detection/threat-detection.component';
import { AlertsComponent } from './core/pages/alerts/alerts.component';
import { AuditComponent } from './core/pages/audit/audit.component';
import { ReportsComponent } from './core/pages/reports/reports.component';
import { UserManagementComponent } from './core/pages/user-management/user-management.component';
import { AuthLayoutComponent } from './layout/auth-layout/auth-layout.component';

export const appRoutes: Routes = [
  {
    path: 'dashboard',
    component: DashboardComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'file-integrity',
    component: FileIntegrityComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'log-monitoring',
    component: LogMonitoringComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'threat-detection',
    component: ThreatDetectionComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'alerts',
    component: AlertsComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'audit',
    component: AuditComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'reports',
    component: ReportsComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'user-management',
    component: UserManagementComponent,
    canActivate: [AuthGuard],
  },
  {
    path: 'login',
    component: AuthLayoutComponent,
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
