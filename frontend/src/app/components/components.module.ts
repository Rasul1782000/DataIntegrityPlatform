import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LoadingSpinnerComponent } from './loading-spinner/loading-spinner.component';
import { FileStatusBadgeComponent } from './file-status-badge/file-status-badge.component';
import { AlertsBadgeComponent } from './alerts-badge/alerts-badge.component';
import { EmptyStateComponent } from './empty-state/empty-state.component';
import { ErrorStateComponent } from './error-state/error-state.component';
import { ConfirmDialogComponent } from './confirm-dialog/confirm-dialog.component';
import { DeleteDialogComponent } from './delete-dialog/delete-dialog.component';
import { TimestampPipe } from './pipes/timestamp.pipe';
import { StatusPipe } from './pipes/status.pipe';
import { SeverityPipe } from './pipes/severity.pipe';
import { FileSizePipe } from './pipes/file-size.pipe';
import { TruncatePipe } from './pipes/truncate.pipe';
import { TruncateDirective } from './directives/truncate.directive';
import { HighlightDirective } from './directives/highlight.directive';
import { FocusDirective } from './directives/focus.directive';

/**
 * Single module for all shared/reusable components, pipes and directives.
 * Every component lives in its own folder (html/scss/ts side by side).
 * Re-exports CommonModule so importing modules get ngIf/ngFor/ngClass/etc.
 */
@NgModule({
  declarations: [
    LoadingSpinnerComponent,
    FileStatusBadgeComponent,
    AlertsBadgeComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    ConfirmDialogComponent,
    DeleteDialogComponent,
    TimestampPipe,
    StatusPipe,
    SeverityPipe,
    FileSizePipe,
    TruncatePipe,
    TruncateDirective,
    HighlightDirective,
    FocusDirective,
  ],
  imports: [
    CommonModule,
  ],
  exports: [
    CommonModule,
    LoadingSpinnerComponent,
    FileStatusBadgeComponent,
    AlertsBadgeComponent,
    EmptyStateComponent,
    ErrorStateComponent,
    ConfirmDialogComponent,
    DeleteDialogComponent,
    TimestampPipe,
    StatusPipe,
    SeverityPipe,
    FileSizePipe,
    TruncatePipe,
    TruncateDirective,
    HighlightDirective,
    FocusDirective,
  ],
})
export class ComponentsModule { }
