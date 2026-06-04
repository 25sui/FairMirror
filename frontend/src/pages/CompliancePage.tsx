import { Button, Card, Col, Divider, List, Progress, Row, Space, Steps, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { getComplianceReport, getReportSummary } from '../services/api';
import type { AuditReportSummary } from '../types/audit';

function downloadReport(report: any, summary?: AuditReportSummary) {
  const blob = new Blob([JSON.stringify({ summary, compliance: report }, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${report.report_id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

function exportPdf() {
  window.print();
}

const reportScope = ['JD 发布前审计', '简历筛选防御', '面试批次公平性', '模型解释与去偏', '合规检查与整改'];
const evidenceChain = [
  '输入材料：JD 文本、简历文本、面试 CSV 批次。',
  '审计引擎：配置化规则库、语义复核、模型归因、群体公平指标。',
  '风险证据：命中位置、风险类型、分值、整改建议和法规映射。',
  '治理输出：审计记录、合规检查、整改路线图、PDF/JSON 留痕。',
];

export function CompliancePage() {
  const [report, setReport] = useState<any>();
  const [summary, setSummary] = useState<AuditReportSummary>();

  useEffect(() => {
    getComplianceReport().then(setReport);
    getReportSummary().then(setSummary);
  }, []);

  if (!report) return <Card loading />;

  return (
    <div className="page-stack report-print-root">
      <section className="hero-panel compact report-cover">
        <div>
          <Tag color="default">正式报告</Tag>
          <h1>招聘公平性审计报告</h1>
          <p>{report.organization} · 报告编号 {report.report_id}</p>
          <p>审计目标：证明招聘流程可量化、可解释、可复核、可整改。</p>
        </div>
        <Space direction="vertical" align="end">
          <Progress type="dashboard" percent={report.readiness_score} strokeColor="#0f766e" />
          <Space className="report-actions">
            <Button onClick={() => downloadReport(report, summary)}>导出 JSON</Button>
            <Button type="primary" onClick={exportPdf}>导出 PDF</Button>
          </Space>
        </Space>
      </section>

      <Row gutter={[18, 18]}>
        <Col xs={24} lg={8}>
          <Card className="glass-card report-section" title="审计范围">
            <List dataSource={reportScope} renderItem={(item) => <List.Item><Tag color="blue">覆盖</Tag>{item}</List.Item>} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card className="glass-card report-section" title="核心结论">
            <Typography.Title level={2}>{summary?.risk_score ?? 71.8}</Typography.Title>
            <Typography.Text type="secondary">综合风险分</Typography.Text>
            <Divider />
            <List dataSource={summary?.key_findings ?? []} renderItem={(item) => <List.Item>{item}</List.Item>} />
          </Card>
        </Col>
        <Col xs={24} lg={8}>
          <Card className="glass-card report-section" title="整改动作">
            <List dataSource={summary?.next_actions ?? []} renderItem={(item) => <List.Item>{item}</List.Item>} />
          </Card>
        </Col>
      </Row>

      <Card className="glass-card report-section" title="证据链">
        <Steps current={3} items={evidenceChain.map((title) => ({ title }))} />
      </Card>

      <Card className="glass-card compliance-report report-section" title="法规检查清单">
        <List
          dataSource={report.items}
          renderItem={(item: any) => (
            <List.Item>
              <Space direction="vertical" size={6}>
                <Space><Tag color={item.status === 'pass' ? 'green' : 'orange'}>{item.status}</Tag><strong>{item.title}</strong><Tag>{item.jurisdiction}</Tag><Tag>{item.code}</Tag></Space>
                <Typography.Text type="secondary">证据：{item.evidence}</Typography.Text>
                <Typography.Text>整改：{item.remediation}</Typography.Text>
              </Space>
            </List.Item>
          )}
        />
      </Card>

      <Card className="glass-card report-section" title="整改路线图">
        <Steps current={1} items={report.roadmap.map((title: string) => ({ title }))} />
      </Card>

      <Row gutter={[18, 18]} className="signature-grid">
        <Col xs={24} md={8}><Card className="glass-card signature-card" title="企业负责人签核">签名：__________<br />日期：__________</Card></Col>
        <Col xs={24} md={8}><Card className="glass-card signature-card" title="HR 负责人签核">签名：__________<br />日期：__________</Card></Col>
        <Col xs={24} md={8}><Card className="glass-card signature-card" title="审计员签核">签名：__________<br />日期：__________</Card></Col>
      </Row>
    </div>
  );
}