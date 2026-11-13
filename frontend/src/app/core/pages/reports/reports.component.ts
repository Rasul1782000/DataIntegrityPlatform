import { Component } from '@angular/core';
import { Report } from '../../../shared/models/report.model';
import { ReportsService } from '../../services/reports.service';

@Component({
  selector: 'app-reports',
  standalone: false,
  templateUrl: './reports.component.html',
  styleUrl: './reports.component.scss'
})
export class ReportsComponent {
  isLoading = true;
  reports: Report[] = [];

  constructor(private reportsService: ReportsService) {}

  ngOnInit(): void {
    this.loadReports();
  }

  private loadReports(): void {
    this.reportsService.getReports().subscribe({
      next: (reports) => {
        this.reports = reports;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading reports:', err);
        this.isLoading = false;
      }
    });
  }

  getReportTypeClass(type: string): string {
    switch (String(type).toLowerCase()) {
      case 'fim': return 'badge bg-primary';
      case 'alerts': return 'badge bg-danger';
      case 'log': return 'badge bg-info text-dark';
      default: return 'badge bg-secondary';
    }
  }
}
