import { Button, Card, Col, List, Progress, Row, Space, Tag, Typography, Input } from 'antd';
import { useEffect, useState } from 'react';
import { EvidenceText } from '../components/EvidenceText';
import { auditJd, getDemo } from '../services/api';
import type { JDAuditResponse } from '../types/audit';

const { TextArea } = Input;

export function JDAuditPage() {
  const [content, setContent] = useState('');
  const [result, setResult] = useState<JDAuditResponse>();

  useEffect(() => {
    getDemo().then((demo) => setContent(demo.jd));
  }, []);

  return (
    <div className="page-stack">
      <Card className="glass-card" title="岗位审计" extra={<Tag color="default">HR</Tag>}>
        <TextArea value={content} onChange={(event) => setContent(event.target.value)} rows={8} />
        <Button className="primary-action" type="primary" onClick={() => auditJd('高级增长产品经理', content).then(setResult)}>检查岗位</Button>
      </Card>

      {result && (
        <Row gutter={[18, 18]}>
          <Col xs={24} md={7}>
            <Card className="glass-card" title="风险分">
              <Progress type="dashboard" percent={result.risk_score} strokeColor="#b45309" />
              <Typography.Paragraph>{result.summary}</Typography.Paragraph>
            </Card>
          </Col>
          <Col xs={24} md={17}>
            <Card className="glass-card" title="问题与建议">
              <List
                dataSource={result.findings}
                renderItem={(item) => (
                  <List.Item>
                    <Space direction="vertical" size={4}>
                      <Space><Tag color={item.level === 'high' ? 'red' : 'orange'}>{item.level}</Tag><strong>{item.text}</strong><span>{item.reason}</span></Space>
                      <Typography.Text type="secondary">建议：{item.suggestion}</Typography.Text>
                    </Space>
                  </List.Item>
                )}
              />
            </Card>
          </Col>
          <Col span={24}>
            <Card className="glass-card" title="证据对照">
              <Row gutter={[18, 18]}>
                <Col xs={24} lg={12}>
                  <Typography.Title level={5}>原文命中</Typography.Title>
                  <EvidenceText text={content} findings={result.findings} />
                </Col>
                <Col xs={24} lg={12}>
                  <Typography.Title level={5}>整改版本</Typography.Title>
                  <Typography.Paragraph className="rewritten-box">{result.rewritten}</Typography.Paragraph>
                </Col>
              </Row>
            </Card>
          </Col>
        </Row>
      )}
    </div>
  );
}