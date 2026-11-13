export interface Alert {
  id: string;
  title: string;
  description: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved' | 'false-positive';
  createdAt: Date;
  resolvedAt?: Date;
  assignedTo?: string;
  deduplicationKey?: string;
}