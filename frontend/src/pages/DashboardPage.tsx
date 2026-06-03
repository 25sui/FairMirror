import { Card, Col, List, Progress, Row, Space, Statistic, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getAuditJobs, getDashboardSummary, getReportSummary, getRoles } from '../services/api';
import type { AuditJobSummary, AuditReportSummary, RoleProfile } from '../types/audit';

export function DashboardPage() {
  const [data, setData] = useState<any>();
  const [roles, setRoles] = useState<RoleProfile[]>([]);
  const [jobs, setJobs] = useState<AuditJobSummary[]>([]);
  const [report, setReport] = useState<AuditReportSummary>();

  useEffect(() => {
    Promise.all([getDashboardSummary(), getRoles(), getAuditJobs(), getReportSummary()])
      .then(([summary, roleProfiles, auditJobs, reportSummary]) => {
        setData(summary);
        setRoles(roleProfiles);
        setJobs(auditJobs);
        setReport(reportSummary);
      })
      .catch(() => undefined);
  }, []);

  if (!data) return <Card loading />;

  return (
    <div className="page-stack">
      <section className="hero-panel">
        <div>
          <Tag color="default">概览</Tag>
          <h1>招聘公平总览</h1>
          <p>集中查看岗位、简历、面试和合规风险，定位需要处理的环节。</p>
        </div>
        <Progress type="dashboard" percent={data.fairness_index} strokeColor="#0f766e" />
      </section>

      <Row gutter={[18, 18]}>
        <Col xs={24} md={8}><Card className="glass-card"><Statistic title="已完成审计" value={data.audits_completed} suffix="次" /></Card></Col>
        <Col xs={24} md={8}><Card className="glass-card"><Statistic title="待处理风险" value={data.open_risks} valueStyle={{ color: '#b45309' }} /></Card></Col>
        <Col xs={24} md={8}><Card className="glass-card"><Statistic title="合规就绪度" value={data.compliance_readiness} suffix="%" /></Card></Col>
      </Row>

      <Row gutter={[18, 18]}>
        <Col xs={24} lg={12}>
          <Card title="风险分布" className="glass-card">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={data.bias_heatmap}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="type" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="jd" name="岗位" fill="#0f766e" radius={[8, 8, 0, 0]} />
                <Bar dataKey="resume" name="简历" fill="#64748b" radius={[8, 8, 0, 0]} />
                <Bar dataKey="interview" name="面试" fill="#cbd5e1" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="通过率趋势" className="glass-card">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={data.pass_rate_trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="majority" name="基准组" stroke="#0f766e" strokeWidth={3} />
                <Line type="monotone" dataKey="protected" name="对照组" stroke="#64748b" strokeWidth={3} />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>

      <Row gutter={[18, 18]}>
        <Col xs={24} lg={12}>
          <Card title="角色入口" className="glass-card">
            <Row gutter={[12, 12]}>
              {roles.map((role) => (
                <Col xs={24} md={12} key={role.role}>
                  <div className="role-tile">
                    <Tag color="default">{role.label}</Tag>
                    <Typography.Title level={5}>{role.scope}</Typography.Title>
                    <Typography.Text type="secondary">入口：{role.default_view}</Typography.Text>
                  </div>
                </Col>
              ))}
            </Row>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card title="审计任务" className="glass-card">
            <List
              dataSource={jobs}
              renderItem={(job) => (
                <List.Item>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <Space wrap>
                      <Tag color={job.status === 'completed' ? 'green' : 'orange'}>{job.status}</Tag>
                      <strong>{job.title}</strong>
                    </Space>
                    <Progress percent={Math.round(job.risk_score)} strokeColor={job.risk_score > 60 ? '#b45309' : '#0f766e'} />
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>
      </Row>

      {report && (
        <Card title="报告摘要" className="glass-card">
          <Row gutter={[18, 18]}>
            <Col xs={24} md={8}>
              <Progress type="dashboard" percent={report.risk_score} strokeColor="#b45309" />
            </Col>
            <Col xs={24} md={16}>
              <Typography.Title level={4}>{report.title}</Typography.Title>
              <Space wrap>{report.coverage.map((item) => <Tag key={item}>{item}</Tag>)}</Space>
              <List size="small" dataSource={report.next_actions} renderItem={(item) => <List.Item>{item}</List.Item>} />
            </Col>
          </Row>
        </Card>
      )}
    </div>
  );
}