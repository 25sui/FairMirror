export type BiasFinding = {
  type: string;
  level: 'high' | 'medium' | 'low';
  score: number;
  text: string;
  position: [number, number];
  reason: string;
  suggestion: string;
  compliance: string;
  source: 'rule' | 'semantic_review';
  rule_id?: string;
};

export type ExplanationFactor = {
  feature: string;
  direction: 'risk' | 'protective';
  impact: number;
  explanation: string;
};

export type JDAuditResponse = {
  audit_id: string;
  title: string;
  risk_score: number;
  inclusive_score: number;
  summary: string;
  findings: BiasFinding[];
  explanations: ExplanationFactor[];
  rewritten: string;
  compliance_flags: string[];
};

export type ResumeAuditResponse = {
  audit_id: string;
  candidate_name: string;
  risk_score: number;
  ats_scores: { system: string; pass_rate: number; reason: string }[];
  findings: BiasFinding[];
  rewritten: string;
  anonymity_tips: string[];
  explanations: ExplanationFactor[];
};

export type InterviewRecord = {
  candidate_id: string;
  group: string;
  score: number;
  passed: boolean;
  question_depth: number;
};

export type FairnessMetric = {
  code: string;
  label: string;
  value: number;
  threshold: string;
  status: 'pass' | 'warning' | 'fail';
  explanation: string;
};

export type InterviewAuditResponse = {
  audit_id: string;
  batch_name: string;
  four_fifths_rule: boolean;
  disparate_impact_ratio: number;
  risk_level: string;
  metrics: { group: string; total: number; passed: number; pass_rate: number; average_score: number; average_question_depth: number }[];
  fairness_metrics: FairnessMetric[];
  calculation_notes: string[];
  explanations: ExplanationFactor[];
  recommendations: string[];
};

export type RoleProfile = {
  role: 'enterprise_admin' | 'hr' | 'candidate' | 'auditor';
  label: string;
  scope: string;
  permissions: string[];
  default_view: string;
};

export type AuditJobSummary = {
  audit_id: string;
  kind: 'jd' | 'resume' | 'interview' | 'compliance';
  title: string;
  owner_role: string;
  status: 'completed' | 'warning' | 'failed';
  risk_score: number;
  created_at: string;
};

export type AuditReportSummary = {
  report_id: string;
  title: string;
  organization: string;
  coverage: string[];
  risk_score: number;
  key_findings: string[];
  next_actions: string[];
};