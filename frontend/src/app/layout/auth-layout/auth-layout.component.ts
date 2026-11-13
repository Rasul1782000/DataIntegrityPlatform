import { Component } from '@angular/core';
import { Router } from '@angular/router';

import { AuthService } from '../../core/services/auth.service';

@Component({
  selector: 'app-auth-layout',
  standalone: false,
  templateUrl: './auth-layout.component.html',
  styleUrl: './auth-layout.component.scss'
})
export class AuthLayoutComponent {
  username = '';
  password = '';
  errorMessage = '';
  isSubmitting = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  onSubmit(form: any): void {
    if (!form.valid || this.isSubmitting) {
      return;
    }
    this.isSubmitting = true;
    this.errorMessage = '';

    this.authService.login(this.username, this.password).subscribe({
      next: (user) => {
        this.isSubmitting = false;
        if (user) {
          this.router.navigate(['/dashboard']);
        } else {
          this.errorMessage = 'Invalid username or password.';
        }
      },
      error: (err) => {
        this.isSubmitting = false;
        console.error('Login failed', err);
        this.errorMessage = 'Login failed. Please check your credentials and try again.';
      }
    });
  }
}
