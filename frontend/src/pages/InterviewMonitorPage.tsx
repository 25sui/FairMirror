import { Card, Col, List, Progress, Row, Space, Statistic, Table, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { auditInterviewDemo } from '../services/api';
import type { InterviewAuditResponse } from '../types/audit';

export function InterviewMonitorPage() {
  const [result, setResult] = useState<InterviewAuditResponse>();

  useEffect(() => {
    auditInterviewDemo().then(setResult);
  }, []);

  if (!result) return <Card loading />;

  return (
    <div className="page-stack">
      <section className="hero-panel compact">
        <div>
          <Tag color={result.four_fifths_rule ? 'green' : 'red'}>{result.four_fifths_rule ? '正常' : '需复核'}</Tag>
          <h1>面试监控</h1>
          <p>{result.batch_name} · 差异影响比 {result.disparate_impact_ratio}</p>
        </div>
        <Statistic title="风险等级" value={result.risk_level} />
      </section>

      <Row gutter={[18, 18]}>
        <Col xs={24} lg={12}>
          <Card className="glass-card" title="群体通过率">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={result.metrics}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="group" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="pass_rate" name="通过率" fill="#0f766e" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </Col>
        <Col xs={24} lg={12}>
          <Card className="glass-card" title="影响因素">
            <List dataSource={result.explanations} renderItem={(item) => <List.Item><Space direction="vertical"><strong>{item.feature}</strong><Progress percent={Math.round(item.impact * 100)} strokeColor="#64748b" /><Typography.Text>{item.explanation}</Typography.Text></Space></List.Item>} />
          </Card>
        </Col>
        <Col span={24}>
          <Card className="glass-card" title="批次明细">
            <Table rowKey="group" dataSource={result.metrics} pagination={false} columns={[{ title: '群体', dataIndex: 'group' }, { title: '样本数', dataIndex: 'total' }, { title: '通过数', dataIndex: 'passed' }, { title: '通过率', dataIndex: 'pass_rate' }, { title: '平均分', dataIndex: 'average_score' }, { title: '追问深度', dataIndex: 'average_question_depth' }]} />
          </Card>
        </Col>
      </Row>
    </div>
  );
}