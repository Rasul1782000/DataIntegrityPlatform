export interface LogSource {
  id: string;
  sourceName: string;
  sourceType: 'windows-event-log' | 'journald' | 'text-file' | 'syslog' | 'other';
  sourcePath: string;
  healthStatus: 'healthy' | 'degraded' | 'failing' | 'disabled';
  lastReadAt?: Date;
  createdAt?: Date;
}
