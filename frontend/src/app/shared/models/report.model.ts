export interface Report {
  id: string;
  title: string;
  type: 'fim' | 'alerts' | 'log';
  generatedAt: Date;
  recordCount: number;
  format: 'CSV' | 'PDF';
  filePath?: string;
  description?: string;
}