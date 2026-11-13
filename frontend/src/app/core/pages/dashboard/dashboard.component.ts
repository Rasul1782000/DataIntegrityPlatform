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
  dashboardSummary: DashboardSummary | undefined;

  // Chart data (populated from the dashboard summary once loaded)
  fileChangesData: any;
  fileChangesOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
  };
  authData: any;
  authOptions: any = {
    responsive: true,
    maintainAspectRatio: false,
  };

  constructor(private dashboardService: DashboardService) {}

  ngOnInit(): void {
    this.dashboardService.getDashboardSummary().subscribe({
      next: (summary) => {
        this.dashboardSummary = summary;
        this.updateCharts(summary);
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading dashboard summary:', err);
        this.isLoading = false;
      }
    });
  }

  private updateCharts(summary: DashboardSummary | undefined): void {
    this.fileChangesData = {
      labels: ['Modified', 'Added', 'Deleted'],
      datasets: [
        {
          label: 'File changes today',
          data: [
            summary?.modifiedFilesToday || 0,
            summary?.addedFilesToday || 0,
            summary?.deletedFilesToday || 0,
          ],
        },
      ],
    };

    this.authData = {
      labels: ['Successful', 'Failed'],
      datasets: [
        {
          label: 'Login attempts',
          data: [summary?.totalLogEvents || 0, summary?.failedLoginAttempts || 0],
        },
      ],
    };
  }

  private getSeverityClass(count: number | undefined): string {
    if (count === undefined || count === null) return 'text-primary';
    if (count >= 100) return 'text-critical';
    if (count >= 25) return 'text-high';
    if (count >= 10) return 'text-warning';
    return 'text-primary';
  }
}
