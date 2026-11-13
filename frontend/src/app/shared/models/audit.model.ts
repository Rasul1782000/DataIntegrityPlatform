export interface AuditLog {
  id: string;
  actorId: string;
  actorUsername: string;
  action: string;
  entityType: string;
  entityId: string;
  previousValue?: string;
  newValue?: string;
  note?: string;
  timestamp: Date;
  previousRecordHash?: string;
  recordHash?: string;
}