import { Directive, ElementRef, Renderer2 } from '@angular/core';

@Directive({
  selector: '[appHighlight]'
})
export class HighlightDirective {
  constructor(private el: ElementRef, private renderer: Renderer2) {}

  highlight(color: string = '#fff3e0'): void {
    this.renderer.setStyle(this.el.nativeElement, 'backgroundColor', color);
  }
}