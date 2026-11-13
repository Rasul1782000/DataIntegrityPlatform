import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-delete-dialog',
  standalone: false,
  templateUrl: './delete-dialog.component.html',
  styleUrl: './delete-dialog.component.scss'
})
export class DeleteDialogComponent {
  @Input() itemName: string = 'item';

  onConfirm(): void {
    // Emit the delete event
    // The parent component handles the actual deletion
  }
}
