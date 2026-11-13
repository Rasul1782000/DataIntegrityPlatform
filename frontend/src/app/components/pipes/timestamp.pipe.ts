import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'timestamp',
  pure: false
})
export class TimestampPipe implements PipeTransform {
  transform(value: string | number | Date): string {
    const date = new Date(value);
    const now = new Date();
    const diffMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
    const diffHours = Math.floor(diffMinutes / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 0) {
      return `${diffDays}d ago`;
    }
    if (diffHours > 0) {
      return `${diffHours}h ago`;
    }
    if (diffMinutes > 0) {
      return `${diffMinutes}m ago`;
    }
    return 'Just now';
  }
}