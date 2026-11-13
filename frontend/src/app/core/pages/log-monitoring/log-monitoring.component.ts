import { Component } from '@angular/core';
import { SecurityEvent } from '../../../shared/models/log-event.model';
import { LogSource } from '../../../shared/models/log-source.model';
import { LogMonitoringService } from '../../services/log-monitoring.service';

@Component({
  selector: 'app-log-monitoring',
  standalone: false,
  templateUrl: './log-monitoring.component.html',
  styleUrl: './log-monitoring.component.scss'
})
export class LogMonitoringComponent {
  isLoading = true;
  logSources: LogSource[] = [];
  displayedEvents: SecurityEvent[] = [];
  isStreaming = false;

  constructor(private logMonitoringService: LogMonitoringService) {}

  ngOnInit(): void {
    this.loadLogSources();
    this.loadDisplayedEvents();
  }

  private loadLogSources(): void {
    this.logMonitoringService.getLogSources().subscribe({
      next: (sources) => {
        this.logSources = sources;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading log sources:', err);
        this.isLoading = false;
      }
    });
  }

  private loadDisplayedEvents(): void {
    this.logMonitoringService.getRecentEvents().subscribe({
      next: (events) => {
        this.displayedEvents = events;
      }
    });
  }

  getSourceTypeClass(sourceType: string): string {
    switch (String(sourceType).toLowerCase()) {
      case 'windows-event-log': return 'badge bg-primary';
      case 'journald': return 'badge bg-info text-dark';
      case 'text-file': return 'badge bg-secondary';
      case 'syslog': return 'badge bg-dark';
      default: return 'badge bg-secondary';
    }
  }

  getHealthClass(healthStatus: string): string {
    switch (String(healthStatus).toLowerCase()) {
      case 'healthy': return 'badge bg-success';
      case 'degraded': return 'badge bg-warning text-dark';
      case 'failing': return 'badge bg-danger';
      case 'disabled': return 'badge bg-secondary';
      default: return 'badge bg-secondary';
    }
  }

  toggleStream(): void {
    this.isStreaming = !this.isStreaming;
  }
}
