import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { RouterModule } from '@angular/router';

import { SidebarComponent } from './sidebar/sidebar.component';
import { TopNavbarComponent } from './top-navbar/top-navbar.component';
import { NotificationIndicatorComponent } from './notification-indicator/notification-indicator.component';
import { GlobalSearchComponent } from './global-search/global-search.component';

/**
 * Single module for the application shell (sidebar, navbar, search,
 * notification indicator).
 */
@NgModule({
  declarations: [
    SidebarComponent,
    TopNavbarComponent,
    NotificationIndicatorComponent,
    GlobalSearchComponent,
  ],
  imports: [
    CommonModule,
    FormsModule,
    RouterModule,
  ],
  exports: [
    SidebarComponent,
    TopNavbarComponent,
    NotificationIndicatorComponent,
    GlobalSearchComponent,
  ],
})
export class LayoutModule { }
