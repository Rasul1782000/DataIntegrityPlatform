import { Component } from '@angular/core';
import { AuditLog } from '../../../shared/models/audit.model';
import { AuditService } from '../../services/audit.service';

@Component({
  selector: 'app-audit',
  standalone: false,
  templateUrl: './audit.component.html',
  styleUrl: './audit.component.scss'
})
export class AuditComponent {
  isLoading = true;
  auditLogs: AuditLog[] = [];
  chainVerified = false;

  constructor(private auditService: AuditService) {}

  ngOnInit(): void {
    this.loadAuditLogs();
  }

  private loadAuditLogs(): void {
    this.auditService.getAuditLogs().subscribe({
      next: (logs) => {
        this.auditLogs = logs;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading audit logs:', err);
        this.isLoading = false;
      }
    });
  }

  getActionClass(action: string): string {
    switch (String(action).toLowerCase()) {
      case 'create':
      case 'created':
        return 'badge bg-success';
      case 'update':
      case 'updated':
        return 'badge bg-warning text-dark';
      case 'delete':
      case 'deleted':
        return 'badge bg-danger';
      default:
        return 'badge bg-secondary';
    }
  }

  onViewDetails(logId: string): void {
    // TODO: Open audit log details view
  }

  verifyChain(): void {
    this.chainVerified = !!this.auditService.verifyChain();
  }
}