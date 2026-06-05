import axios from 'axios';
import type {
  AuditJobSummary,
  AuditReportSummary,
  DebiasingDemoResponse,
  DemoPayload,
  InterviewRecord,
  ModelAuditResponse,
  RoleProfile,
} from '../types/audit';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
});

export async function getDemo(): Promise<DemoPayload> {
  const { data } = await api.get('/demo');
  return data;
}

export async function extractDocument(file: File): Promise<{ filename: string; text: string; characters: number }> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post('/documents/extract', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function auditJd(title: string, content: string) {
  const { data } = await api.post('/jd/audit', { title, content, role: 'hr' });
  return data;
}

export async function auditResume(candidateName: string, content: string, targetRole: string) {
  const { data } = await api.post('/resume/audit', { candidate_name: candidateName, content, target_role: targetRole });
  return data;
}

export async function auditInterview(batchName: string, records: InterviewRecord[]) {
  const { data } = await api.post('/interview/audit', { batch_name: batchName, records });
  return data;
}

export async function auditInterviewDemo() {
  const { data } = await api.get('/interview/demo');
  return data;
}

export async function getComplianceReport() {
  const { data } = await api.get('/compliance/report');
  return data;
}

export async function getDashboardSummary() {
  const { data } = await api.get('/dashboard/summary');
  return data;
}

export async function getRoles(): Promise<RoleProfile[]> {
  const { data } = await api.get('/roles');
  return data;
}

export async function getAuditJobs(): Promise<AuditJobSummary[]> {
  const { data } = await api.get('/audit-jobs');
  return data;
}

export async function getReportSummary(): Promise<AuditReportSummary> {
  const { data } = await api.get('/reports/summary');
  return data;
}

export async function runModelAudit(content: string, scenario: 'jd' | 'resume' = 'jd'): Promise<ModelAuditResponse> {
  const { data } = await api.post('/ai/model-audit', { content, scenario });
  return data;
}

export async function getDebiasingDemo(): Promise<DebiasingDemoResponse> {
  const { data } = await api.get('/ai/debiasing-demo');
  return data;
}
