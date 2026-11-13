import { Component } from '@angular/core';

@Component({
  selector: 'app-global-search',
  standalone:false,
  templateUrl: './global-search.component.html',
  styleUrl: './global-search.component.scss'
})

export class GlobalSearchComponent {
  onFocus(): void {

  }

  onInput(event: Event): void {
    // TODO: Implement global search input
  }
}