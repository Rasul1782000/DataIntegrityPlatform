import { Component } from '@angular/core';
import { FileIntegrityEvent } from '../../../shared/models/file-event.model';
import { FileIntegrityService } from '../../services/file-integrity.service';

@Component({
  selector: 'app-file-integrity',
  standalone: false,
  templateUrl: './file-integrity.component.html',
  styleUrl: './file-integrity.component.scss'
})
export class FileIntegrityComponent {
  isLoading = true;
  monitoredDirectories: any[] = [];
  baselinesCreated = 0;
  recentEvents: FileIntegrityEvent[] = [];

  constructor(private fileIntegrityService: FileIntegrityService) {}

  ngOnInit(): void {
    this.loadMonitoredDirectories();
    this.loadRecentEvents();
    this.loadBaselinesCount();
  }

  private loadMonitoredDirectories(): void {
    this.fileIntegrityService.getMonitoredDirectories().subscribe({
      next: (directories) => {
        this.monitoredDirectories = directories;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading monitored directories:', err);
        this.isLoading = false;
      }
    });
  }

  private loadRecentEvents(): void {
    this.fileIntegrityService.getRecentEvents().subscribe({
      next: (events) => {
        this.recentEvents = events;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading recent events:', err);
        this.isLoading = false;
      }
    });
  }

  private loadBaselinesCount(): void {
    this.fileIntegrityService.getBaselinesCount().subscribe({
      next: (count) => {
        this.baselinesCreated = count;
      }
    });
  }

  getEventTypeClass(eventType: string): string {
    switch (String(eventType).toUpperCase()) {
      case 'CREATED': return 'badge bg-success';
      case 'MODIFIED': return 'badge bg-warning text-dark';
      case 'DELETED': return 'badge bg-danger';
      case 'MOVED': return 'badge bg-info text-dark';
      case 'PERMISSION_CHANGED': return 'badge bg-primary';
      case 'SCAN_ERROR': return 'badge bg-danger';
      default: return 'badge bg-secondary';
    }
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

  registerDirectory(): void {
    // TODO: Open directory registration dialog
  }
}
