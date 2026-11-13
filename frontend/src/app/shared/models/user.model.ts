export interface User {
  id: string;
  username: string;
  email: string;
  role: 'administrator' | 'security-analyst' | 'auditor' | 'viewer';
  isActive: boolean;
  lastLogin?: Date;
  createdAt: Date;
}