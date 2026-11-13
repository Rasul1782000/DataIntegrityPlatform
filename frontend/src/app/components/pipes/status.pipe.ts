import { Pipe, PipeTransform } from '@angular/core';

@Pipe({
  name: 'status',
  pure: false
})
export class StatusPipe implements PipeTransform {
  transform(value: string | boolean): string {
    if (typeof value === 'boolean') {
      return value ? 'Enabled' : 'Disabled';
    }
    switch (String(value).toLowerCase()) {
      case 'true': return 'Enabled';
      case 'false': return 'Disabled';
      case 'created': return 'Created';
      case 'modified': return 'Modified';
      case 'deleted': return 'Deleted';
      case 'active': return 'Active';
      case 'inactive': return 'Inactive';
      default: return String(value);
    }
  }
}