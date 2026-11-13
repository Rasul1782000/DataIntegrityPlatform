export interface FileIntegrityEvent {
  id: string;
  directoryId: string;
  directoryName?: string;
  relativePath: string;
  eventType: 'CREATED' | 'MODIFIED' | 'DELETED' | 'MOVED' | 'PERMISSION_CHANGED' | 'SCAN_ERROR';
  previousHash?: string;
  currentHash?: string;
  fileSize?: number;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved';
  detectedAt: Date;
  investigationStatus?: string;
  authorizedReason?: string;
}