export enum BiasLevel {
  HIGH = 'high',
  MEDIUM = 'medium',
  LOW = 'low',
}

export enum BiasType {
  GENDER = 'gender',
  AGE = 'age',
  EDUCATION = 'education',
  REGION = 'region',
  RACE = 'race',
  APPEARANCE = 'appearance',
}

export interface BiasCheckResult {
  type: BiasType;
  score: number;
  level: BiasLevel;
  text: string;
  position: number[];
  suggestion: string;
  severity: number;
}

export interface JDAuditResponse {
  bias_results: BiasCheckResult[];
  overall_score: number;
  overall_level: BiasLevel;
  suggestions: string[];
  report_url?: string;
  audit_timestamp: string;
}

export interface SensitiveField {
  field_name: string;
  content: string;
  risk_level: BiasLevel;
  suggestion: string;
}

export interface ATSResult {
  system_name: string;
  pass_probability: number;
  key_factors: string[];
}

export interface ResumeScanResponse {
  sensitive_fields: SensitiveField[];
  ats_results: ATSResult[];
  overall_risk_level: BiasLevel;
  rewritten_resume?: string;
  scan_timestamp: string;
}

export interface FairnessMetrics {
  group_pass_rates: Record<string, number>;
  four_fifths_rule_passed: boolean;
  disparate_impact_ratio: number;
  shap_key_features: string[];
  bias_risk_level: BiasLevel;
  recommendations: string[];
}

export interface InterviewAnalysisResponse {
  fairness_metrics: FairnessMetrics;
  analysis_timestamp: string;
  report_url?: string;
}

export interface ComplianceCheckItem {
  item_id: string;
  description: string;
  regulation: string;
  passed: boolean;
  details?: string;
}

export interface ComplianceReport {
  regulation_type: string;
  company_id: number;
  check_items: ComplianceCheckItem[];
  overall_passed: boolean;
  compliance_score: number;
  generated_at: string;
}

export interface User {
  id: number;
  email: string;
  username: string;
  role: string;
  company_id?: number;
  created_at: string;
  is_active: boolean;
}

export interface DashboardMetrics {
  total_jds_audited: number;
  total_resumes_scanned: number;
  total_interviews_analyzed: number;
  average_bias_score: number;
  compliance_rate: number;
  appeals_pending: number;
  recent_alerts: any[];
}
