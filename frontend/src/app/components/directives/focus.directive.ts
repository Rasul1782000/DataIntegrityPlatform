import { Directive, ElementRef, OnInit, OnDestroy } from '@angular/core';

@Directive({
  selector: '[appFocus]'
})
export class FocusDirective implements OnInit, OnDestroy {
  private focusListener: () => void;
  private blurListener: () => void;

  constructor(private el: ElementRef) {}

  ngOnInit(): void {
    this.focusListener = () => this.el.nativeElement.classList.add('focused');
    this.blurListener = () => this.el.nativeElement.classList.remove('focused');

    this.el.nativeElement.addEventListener('focus', this.focusListener);
    this.el.nativeElement.addEventListener('blur', this.blurListener);
  }

  ngOnDestroy(): void {
    this.el.nativeElement.removeEventListener('focus', this.focusListener);
    this.el.nativeElement.removeEventListener('blur', this.blurListener);
  }
}