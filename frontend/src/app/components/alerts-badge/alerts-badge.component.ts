import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-alerts-badge',
  standalone: false,
  templateUrl: './alerts-badge.component.html',
  styleUrl: './alerts-badge.component.scss'
})

export class AlertsBadgeComponent {
  @Input() severity: string = 'medium';
  @Input() label: string = 'Alert';

  get severityClass(): string {
    switch (this.severity) {
      case 'critical': return 'critical';
      case 'high': return 'high';
      case 'medium': return 'medium';
      case 'low': return 'low';
      default: return 'medium';
    }
  }
}