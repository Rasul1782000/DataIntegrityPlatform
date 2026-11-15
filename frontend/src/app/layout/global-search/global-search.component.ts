import { Component, ElementRef, HostListener, ViewChild } from '@angular/core';

@Component({
  selector: 'app-global-search',
  standalone:false,
  templateUrl: './global-search.component.html',
  styleUrl: './global-search.component.scss'
})

export class GlobalSearchComponent {
  @ViewChild('searchInput') searchInput?: ElementRef<HTMLInputElement>;

  onFocus(): void {

  }

  onInput(event: Event): void {
    // TODO: Implement global search input
  }

  // Focus the search field with Ctrl+K / Cmd+K from anywhere
  @HostListener('document:keydown', ['$event'])
  onKeydown(event: KeyboardEvent): void {
    if ((event.ctrlKey || event.metaKey) && String(event.key).toLowerCase() === 'k') {
      event.preventDefault();
      this.searchInput?.nativeElement.focus();
    }
  }
}
