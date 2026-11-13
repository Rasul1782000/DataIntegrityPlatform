export interface Threat {
  id: string;
  threatType: 'brute-force' | 'privilege-escalation' | 'suspicious-ip' | 'malware' | 'other';
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'new' | 'under-investigation' | 'resolved' | 'false-positive';
  sourceIp: string;
  firstSeenAt: Date;
  lastSeenAt: Date;
  associatedUsernames: string[];
  triggeredDetectionRule?: string;
  investigationNotes?: string;
  assignedTo?: string;
}