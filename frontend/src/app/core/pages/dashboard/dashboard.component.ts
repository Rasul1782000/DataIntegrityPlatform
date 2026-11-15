import { Component } from '@angular/core';
import { DashboardSummary } from '../../../shared/models/dashboard-summary.model';
import { DashboardService } from '../../services/dashboard.service';

@Component({
  selector: 'app-dashboard',
  standalone: false,
  templateUrl: './dashboard.component.html',
  styleUrl: './dashboard.component.scss'
})
export class DashboardComponent {
  isLoading = true;
  hasError = false;
  dashboardSummary: DashboardSummary | undefined;

  // Chart data (populated from the dashboard summary once loaded)
  fileChangesData: any;
  fileChangesOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
    },
    scales: {
      y: { beginAtZero: true, ticks: { precision: 0 } },
    },
  };
  authData: any;
  authOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
    cutout: '65%',
    plugins: {
      legend: { position: 'bottom' },
    },
  };

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.loadData();
  }

  loadData(): void {
    this.isLoading = true;
    this.hasError = false;

    this.dashboardService.getDashboardSummary().subscribe({
      next: (summary) => {
        this.dashboardSummary = summary;
        this.updateCharts(summary);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading dashboard summary:', err);
        this.isLoading = false;
        this.hasError = true;
      }
    });
  }

  private updateCharts(summary: DashboardSummary | undefined): void {
    const modified = summary?.modifiedFilesToday || 0;
    const added = summary?.addedFilesToday || 0;
    const deleted = summary?.deletedFilesToday || 0;

    this.fileChangesData = {
      labels: ['Modified', 'Added', 'Deleted'],
      datasets: [
        {
          label: 'File changes today',
          data: [modified, added, deleted],
          backgroundColor: ['#d97706', '#16a34a', '#dc2626'],
          borderRadius: 6,
          maxBarThickness: 64,
        },
      ],
    };

    // Successful logins = total log events that were not failed attempts
    const failed = summary?.failedLoginAttempts || 0;
    const successful = Math.max((summary?.totalLogEvents || 0) - failed, 0);

    this.authData = {
      labels: ['Successful', 'Failed'],
      datasets: [
        {
          data: [successful, failed],
          backgroundColor: ['#16a34a', '#dc2626'],
          borderWidth: 0,
          hoverOffset: 6,
        },
      ],
    };
  }

  getSeverityClass(count: number | undefined): string {
    if (count === undefined || count === null) return 'text-primary';
    if (count >= 100) return 'text-critical';
    if (count >= 25) return 'text-high';
    if (count >= 10) return 'text-warning';
    return 'text-primary';
  }
}
