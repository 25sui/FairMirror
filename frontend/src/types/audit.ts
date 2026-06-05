export type BiasFinding = {
  type: string;
  level: 'high' | 'medium' | 'low';
  score: number;
  text: string;
  position: [number, number];
  reason: string;
  suggestion: string;
  compliance: string;
  source: 'rule' | 'semantic_review' | 'model';
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

export type ModelAuditResponse = {
  audit_id: string;
  scenario: 'jd' | 'resume';
  model_name: string;
  model_version: string;
  runtime_mode: 'transformers' | 'local_surrogate';
  status: string;
  risk_score: number;
  findings: BiasFinding[];
  token_contributions: {
    token: string;
    position: [number, number];
    label: string;
    contribution: number;
    direction: 'risk' | 'protective';
  }[];
  summary: string;
};

export type DebiasingDemoResponse = {
  demo_id: string;
  objective: string;
  sensitive_attribute: string;
  baseline: Record<string, number>;
  debiased: Record<string, number>;
  metrics: {
    metric: string;
    label: string;
    baseline: number;
    debiased: number;
    delta: number;
    interpretation: string;
  }[];
  training_trace: { epoch: number; predictor_loss: number; adversary_accuracy: number; fairness_penalty: number }[];
  sample_preview: {
    candidate_id: string;
    protected_group: boolean;
    qualified: boolean;
    baseline_passed: boolean;
    debiased_passed: boolean;
  }[];
};

export type CompetitionJdSample = {
  sample_id: string;
  title: string;
  job_family?: string;
  city?: string;
  salary?: string;
  education?: string;
  years?: string;
  company?: string;
  source: string;
  risk_tags: string[];
  content: string;
};

export type CompetitionResumeSample = {
  sample_id: string;
  candidate_name: string;
  quality_label?: string;
  target_role: string;
  gender?: string;
  age?: string;
  education?: string;
  city?: string;
  work_years?: string;
  source: string;
  risk_tags: string[];
  content: string;
};

export type DemoPayload = {
  jd: string;
  resume: string;
  interview_records: InterviewRecord[];
  competition_samples: {
    source_file: string;
    derived_files: { jd: string; resume: string };
    jd: CompetitionJdSample[];
    resume: CompetitionResumeSample[];
    stats: { jd_count: number; resume_count: number };
  };
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