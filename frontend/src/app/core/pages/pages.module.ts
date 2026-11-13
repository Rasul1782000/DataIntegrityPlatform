import { NgModule } from '@angular/core';

import { ComponentsModule } from '../../components/components.module';

import { DashboardComponent } from './dashboard/dashboard.component';
import { AlertsComponent } from './alerts/alerts.component';
import { AuditComponent } from './audit/audit.component';
import { FileIntegrityComponent } from './file-integrity/file-integrity.component';
import { LogMonitoringComponent } from './log-monitoring/log-monitoring.component';
import { ReportsComponent } from './reports/reports.component';
import { ThreatDetectionComponent } from './threat-detection/threat-detection.component';
import { UserManagementComponent } from './user-management/user-management.component';

/**
 * Single module for all application pages.
 * Imports ComponentsModule so pages can use shared components, pipes and directives.
 */
@NgModule({
  declarations: [
    DashboardComponent,
    AlertsComponent,
    AuditComponent,
    FileIntegrityComponent,
    LogMonitoringComponent,
    ReportsComponent,
    ThreatDetectionComponent,
    UserManagementComponent,
  ],
  imports: [
    ComponentsModule,
  ],
})
export class PagesModule { }
