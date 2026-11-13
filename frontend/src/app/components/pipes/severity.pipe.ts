import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'severity',
  pure: false
})
export class SeverityPipe implements PipeTransform {
  transform(value: string): string {
    switch (value?.toLowerCase()) {
      case 'critical': return 'Critical';
      case 'high': return 'High';
      case 'medium': return 'Medium';
      case 'low': return 'Low';
      case 'informational': return 'Informational';
      default: return value || 'Medium';
    }
  }
}