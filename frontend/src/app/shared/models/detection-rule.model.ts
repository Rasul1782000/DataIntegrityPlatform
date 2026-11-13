export interface DetectionRule {
  id: string;
  ruleName: string;
  ruleType: string;
  description?: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  threshold?: number;
  enabled: boolean;
  createdAt?: Date;
}
