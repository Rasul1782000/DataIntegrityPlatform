import { Component } from '@angular/core';
import { Alert } from '../../../shared/models/alert.model';
import { AlertsService } from '../../services/alerts.service';

@Component({
  selector: 'app-alerts',
  standalone: false,
  templateUrl: './alerts.component.html',
  styleUrl: './alerts.component.scss'
})
export class AlertsComponent {
  isLoading = true;
  alerts: Alert[] = [];

  summaryCounts = {
    critical: 0,
    high: 0,
    medium: 0,
    low: 0,
  };

  constructor(private alertsService: AlertsService) {}

  ngOnInit(): void {
    this.loadAlerts();
  }

  private loadAlerts(): void {
    this.alertsService.getAlerts().subscribe({
      next: (alerts) => {
        this.alerts = alerts;
        this.isLoading = false;
        this.updateSummaryCounts(alerts);
      },
      error: (err) => {
        console.error('Error loading alerts:', err);
        this.isLoading = false;
      }
    });
  }

  private updateSummaryCounts(alerts: Alert[]): void {
    this.summaryCounts = {
      critical: alerts.filter(a => a.severity === 'critical').length,
      high: alerts.filter(a => a.severity === 'high').length,
      medium: alerts.filter(a => a.severity === 'medium').length,
      low: alerts.filter(a => a.severity === 'low').length,
    };
  }

  getSeverityClass(severity: string): string {
    switch (String(severity).toLowerCase()) {
      case 'critical': return 'badge bg-danger';
      case 'high': return 'badge bg-warning text-dark';
      case 'medium': return 'badge bg-primary';
      case 'low': return 'badge bg-secondary';
      default: return 'badge bg-secondary';
    }
  }

  getStatusClass(status: string): string {
    switch (String(status).toLowerCase()) {
      case 'new': return 'badge bg-danger';
      case 'acknowledged': return 'badge bg-warning text-dark';
      case 'investigating': return 'badge bg-primary';
      case 'resolved': return 'badge bg-success';
      case 'false-positive': return 'badge bg-secondary';
      default: return 'badge bg-secondary';
    }
  }
}
