import { NgModule } from '@angular/core';
import { NgChartsModule } from 'ng2-charts';

import { ComponentsModule } from '../../components/components.module';

import { DashboardComponent } from './dashboard/dashboard.component';
import { AlertsComponent } from './alerts/alerts.component';
import { AuditComponent } from './audit/audit.component';
import { FileIntegrityComponent } from './file-integrity/file-integrity.component';
import { LogMonitoringComponent } from './log-monitoring/log-monitoring.component';
import { ReportsComponent } from './reports/reports.component';
import { ThreatDetectionComponent } from './threat-detection/threat-detection.component';
import { UserManagementComponent } from './user-management/user-management.component';

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
    NgChartsModule,
  ],
})
export class PagesModule { }
