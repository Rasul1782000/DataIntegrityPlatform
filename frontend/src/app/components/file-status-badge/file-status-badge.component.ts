import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-file-status-badge',
  standalone: false,
  templateUrl: './file-status-badge.component.html',
  styleUrl: './file-status-badge.component.scss'
})
export class FileStatusBadgeComponent {
  @Input() status: string = 'modified';
  @Input() label: string = 'Status';

  get statusClass(): string {
    switch (this.status) {
      case 'created': return 'created';
      case 'modified': return 'modified';
      case 'deleted': return 'deleted';
      case 'baseline': return 'baseline';
      default: return 'modified';
    }
  }
}