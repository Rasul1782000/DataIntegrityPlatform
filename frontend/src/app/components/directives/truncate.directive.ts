import { Directive, ElementRef, Input, OnChanges, SimpleChanges } from '@angular/core';

@Directive({
  selector: '[appTruncate]'
})
export class TruncateDirective implements OnChanges {
  @Input() appTruncate: string = '';

  private originalText: string;

  constructor(private elementRef: ElementRef) {
    this.originalText = this.elementRef.nativeElement.textContent || this.elementRef.nativeElement.innerText || '';
  }

  ngOnChanges(changes: SimpleChanges): void {
    if (changes.appTruncate && this.appTruncate.length > 50) {
      const truncated = this.appTruncate.substring(0, 50) + '...';
      this.elementRef.nativeElement.textContent = truncated;
    } else {
      this.elementRef.nativeElement.textContent = this.appTruncate || this.originalText;
    }
  }
}