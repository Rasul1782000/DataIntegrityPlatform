import { Component } from '@angular/core';
import { User } from '../../../shared/models/user.model';
import { UserManagementService } from '../../services/user-management.service';

@Component({
  selector: 'app-user-management',
  standalone: false,
  templateUrl: './user-management.component.html',
  styleUrl: './user-management.component.scss'
})
export class UserManagementComponent {
  isLoading = true;
  users: User[] = [];

  constructor(private userManagementService: UserManagementService) {}

  ngOnInit(): void {
    this.loadUsers();
  }

  private loadUsers(): void {
    this.userManagementService.getUsers().subscribe({
      next: (users) => {
        this.users = users;
        this.isLoading = false;
      },
      error: (err) => {
        console.error('Error loading users:', err);
        this.isLoading = false;
      }
    });
  }

  getRoleClass(role: string): string {
    switch (String(role).toLowerCase()) {
      case 'administrator': return 'badge bg-danger';
      case 'security-analyst': return 'badge bg-primary';
      case 'auditor': return 'badge bg-info text-dark';
      case 'viewer': return 'badge bg-secondary';
      default: return 'badge bg-secondary';
    }
  }

  getStatusClass(isActive: boolean): string {
    return isActive ? 'badge bg-success' : 'badge bg-secondary';
  }
}
