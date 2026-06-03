import axios from 'axios';
import type { AuditJobSummary, AuditReportSummary, RoleProfile } from '../types/audit';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000';

export const api = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 10000,
});

export async function getDemo() {
  const { data } = await api.get('/demo');
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