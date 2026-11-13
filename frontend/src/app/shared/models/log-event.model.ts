export interface SecurityEvent {
  id: string;
  sourceId: string;
  sourceEventId?: string;
  eventCategory: 'authentication' | 'privilege-escalation' | 'brute-force' | 'suspicious-login' | 'other';
  username?: string;
  sourceIp?: string;
  normalizedTimestamp: Date;
  eventDescription: string;
  rawEventReference?: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'acknowledged' | 'investigating' | 'resolved';
}