import { Button, Card, Col, List, Progress, Row, Space, Tag, Typography, Input } from 'antd';
import { useEffect, useState } from 'react';
import { auditResume, getDemo } from '../services/api';
import type { ResumeAuditResponse } from '../types/audit';

const { TextArea } = Input;

export function ResumeShieldPage() {
  const [content, setContent] = useState('');
  const [result, setResult] = useState<ResumeAuditResponse>();

  useEffect(() => {
    getDemo().then((demo) => setContent(demo.resume));
  }, []);

  return (
    <div className="page-stack">
      <Card className="glass-card" title="简历检查" extra={<Tag color="default">求职者</Tag>}>
        <TextArea value={content} onChange={(event) => setContent(event.target.value)} rows={8} />
        <Button className="primary-action" type="primary" onClick={() => auditResume('张敏', content, '增长产品经理').then(setResult)}>检查简历</Button>
      </Card>

      {result && (
        <Row gutter={[18, 18]}>
          <Col xs={24} lg={10}>
            <Card className="glass-card" title="筛选通过率">
              <List dataSource={result.ats_scores} renderItem={(item) => <List.Item><Space direction="vertical" style={{ width: '100%' }}><strong>{item.system}</strong><Progress percent={item.pass_rate} strokeColor="#0f766e" /><Typography.Text type="secondary">{item.reason}</Typography.Text></Space></List.Item>} />
            </Card>
          </Col>
          <Col xs={24} lg={14}>
            <Card className="glass-card" title="敏感信息">
              <List dataSource={result.findings} renderItem={(item) => <List.Item><Space direction="vertical"><Space><Tag color="orange">{item.type}</Tag><strong>{item.text}</strong></Space><Typography.Text>{item.suggestion}</Typography.Text></Space></List.Item>} />
            </Card>
          </Col>
          <Col span={24}>
            <Card className="glass-card" title="匿名化版本">
              <Typography.Paragraph className="rewritten-box">{result.rewritten}</Typography.Paragraph>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
}