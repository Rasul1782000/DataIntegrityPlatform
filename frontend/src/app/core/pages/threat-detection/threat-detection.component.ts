import { Component } from '@angular/core';
import { DetectionRule } from '../../../shared/models/detection-rule.model';
import { Threat } from '../../../shared/models/threat.model';
import { ThreatDetectionService } from '../../services/threat-detection.service';

@Component({
  selector: 'app-threat-detection',
  standalone: false,
  templateUrl: './threat-detection.component.html',
  styleUrl: './threat-detection.component.scss'
})
export class ThreatDetectionComponent {
  isLoading = true;
  detectionRules: DetectionRule[] = [];
  suspiciousIPs: Threat[] = [];

  constructor(private threatDetectionService: ThreatDetectionService) {}

  ngOnInit(): void {
    this.loadDetectionRules();
    this.loadSuspiciousIPs();
  }

  private loadDetectionRules(): void {
    this.threatDetectionService.getDetectionRules().subscribe({
      next: (rules) => {
        this.detectionRules = rules;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading detection rules:', err);
        this.isLoading = false;
      }
    });
  }

  private loadSuspiciousIPs(): void {
    this.threatDetectionService.getSuspiciousIPs().subscribe({
      next: (ips) => {
        this.suspiciousIPs = ips;
      }
    });
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

  getThreatLevelClass(severity: string): string {
    switch (String(severity).toLowerCase()) {
      case 'critical': return 'badge bg-danger';
      case 'high': return 'badge bg-warning text-dark';
      case 'medium': return 'badge bg-info text-dark';
      case 'low': return 'badge bg-success';
      default: return 'badge bg-secondary';
    }
  }
}
