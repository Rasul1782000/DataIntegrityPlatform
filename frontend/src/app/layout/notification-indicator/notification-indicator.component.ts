import { Component, signal } from '@angular/core';

@Component({
  selector: 'app-notification-indicator',
  standalone:false,
  templateUrl: './notification-indicator.component.html',
  styleUrl: './notification-indicator.component.scss'
})
export class NotificationIndicatorComponent {
  // Signal for real-time updates
  health = signal('online');
}