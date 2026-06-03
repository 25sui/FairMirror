import { Button, Card, List, Progress, Space, Steps, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { getComplianceReport } from '../services/api';

function downloadReport(report: any) {
  const blob = new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `${report.report_id}.json`;
  link.click();
  URL.revokeObjectURL(url);
}

export function CompliancePage() {
  const [report, setReport] = useState<any>();

  useEffect(() => {
    getComplianceReport().then(setReport);
  }, []);

  if (!report) return <Card loading />;

  return (
    <div className="page-stack">
      <section className="hero-panel compact">
        <div>
          <Tag color="default">合规</Tag>
          <h1>合规报告</h1>
          <p>{report.organization} · 报告编号 {report.report_id}</p>
        </div>
        <Progress type="dashboard" percent={report.readiness_score} strokeColor="#0f766e" />
      </section>

      <Card className="glass-card" title="检查清单" extra={<Button onClick={() => downloadReport(report)}>导出报告</Button>}>
        <List
          dataSource={report.items}
          renderItem={(item: any) => (
            <List.Item>
              <Space direction="vertical">
                <Space><Tag color={item.status === 'pass' ? 'green' : 'orange'}>{item.status}</Tag><strong>{item.title}</strong><Tag>{item.jurisdiction}</Tag></Space>
                <Typography.Text type="secondary">证据：{item.evidence}</Typography.Text>
                <Typography.Text>整改：{item.remediation}</Typography.Text>
              </Space>
            </List.Item>
          )}
        />
      </Card>

      <Card className="glass-card" title="整改路线图">
        <Steps current={1} items={report.roadmap.map((title: string) => ({ title }))} />
      </Card>
    </div>
  );
}