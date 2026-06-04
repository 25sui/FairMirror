import { Button, Card, Col, List, Progress, Row, Select, Space, Statistic, Table, Tag, Typography } from 'antd';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { getDebiasingDemo, runModelAudit } from '../services/api';
import type { DebiasingDemoResponse, ModelAuditResponse } from '../types/audit';

const sampleTexts = {
  jd: '我们是年轻团队，希望候选人精力充沛，毕业不超过3年，985/211 优先，能长期高强度加班。',
  resume: '候选人女，河南籍，32岁，已婚已育。曾因家庭原因有2年职业空窗期，简历含个人照片。',
};

function statusColor(value: string) {
  if (value === 'transformers') return 'green';
  return 'blue';
}

function booleanTag(value: boolean) {
  return <Tag color={value ? 'green' : 'red'}>{value ? '通过' : '未通过'}</Tag>;
}

export function AITechBarrierPage() {
  const [scenario, setScenario] = useState<'jd' | 'resume'>('jd');
  const [modelResult, setModelResult] = useState<ModelAuditResponse>();
  const [debiasingResult, setDebiasingResult] = useState<DebiasingDemoResponse>();
  const [loading, setLoading] = useState(false);

  const runAudit = async (nextScenario = scenario) => {
    setLoading(true);
    try {
      const result = await runModelAudit(sampleTexts[nextScenario], nextScenario);
      setModelResult(result);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    runAudit('jd');
    getDebiasingDemo().then(setDebiasingResult);
  }, []);

  return (
    <div className="page-stack">
      <section className="hero-panel compact">
        <div>
          <Tag color="purple">技术壁垒</Tag>
          <h1>模型解释与对抗去偏</h1>
          <p>把规则审计扩展为“模型来源、归因证据、去偏前后对比”的算法演示模块。</p>
        </div>
        <Space>
          <Select
            value={scenario}
            onChange={(value) => {
              setScenario(value);
              runAudit(value);
            }}
            options={[{ value: 'jd', label: '岗位文本' }, { value: 'resume', label: '简历文本' }]}
          />
          <Button type="primary" loading={loading} onClick={() => runAudit()}>运行模型审计</Button>
        </Space>
      </section>

      <Row gutter={[18, 18]}>
        <Col xs={24} lg={8}>
          <Card className="glass-card" title="模型状态">
            {modelResult ? (
              <Space direction="vertical" size="middle">
                <Tag color={statusColor(modelResult.runtime_mode)}>{modelResult.runtime_mode}</Tag>
                <Statistic title="模型风险分" value={modelResult.risk_score} precision={1} suffix="/100" />
                <Typography.Text>{modelResult.status}</Typography.Text>
                <Typography.Text type="secondary">{modelResult.model_name} · {modelResult.model_version}</Typography.Text>
              </Space>
            ) : <Card loading />}
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card className="glass-card" title="Token/短语归因">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={modelResult?.token_contributions ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="token" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="contribution" name="贡献度" fill="#7c3aed" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
            <Typography.Paragraph style={{ marginBottom: 0 }}>{modelResult?.summary}</Typography.Paragraph>
          </Card>
        </Col>

        <Col span={24}>
          <Card className="glass-card" title="模型发现">
            <Table
              rowKey={(record) => `${record.source}-${record.text}-${record.position.join('-')}`}
              dataSource={modelResult?.findings ?? []}
              pagination={false}
              columns={[
                { title: '风险类型', dataIndex: 'type' },
                { title: '命中证据', dataIndex: 'text' },
                { title: '来源', dataIndex: 'source', render: (value) => <Tag color="purple">{value}</Tag> },
                { title: '分数', dataIndex: 'score' },
                { title: '建议', dataIndex: 'suggestion' },
              ]}
            />
          </Card>
        </Col>

        <Col xs={24} lg={10}>
          <Card className="glass-card" title="去偏前后指标">
            <List
              dataSource={debiasingResult?.metrics ?? []}
              renderItem={(item) => (
                <List.Item>
                  <Space direction="vertical" style={{ width: '100%' }}>
                    <strong>{item.label}</strong>
                    <Space>
                      <Tag>baseline {item.baseline}</Tag>
                      <Tag color={item.delta >= 0 ? 'green' : 'orange'}>debiased {item.debiased}</Tag>
                      <Tag color="blue">Δ {item.delta}</Tag>
                    </Space>
                    <Progress percent={Math.round(Math.min(1, Math.max(0, item.debiased)) * 100)} strokeColor="#0f766e" />
                    <Typography.Text type="secondary">{item.interpretation}</Typography.Text>
                  </Space>
                </List.Item>
              )}
            />
          </Card>
        </Col>

        <Col xs={24} lg={14}>
          <Card className="glass-card" title="训练过程演示">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={debiasingResult?.training_trace ?? []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="epoch" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="predictor_loss" name="预测损失" stroke="#0f766e" />
                <Line type="monotone" dataKey="adversary_accuracy" name="对抗者准确率" stroke="#7c3aed" />
                <Line type="monotone" dataKey="fairness_penalty" name="公平惩罚" stroke="#f97316" />
              </LineChart>
            </ResponsiveContainer>
            <Typography.Text type="secondary">目标函数：{debiasingResult?.objective}</Typography.Text>
          </Card>
        </Col>

        <Col span={24}>
          <Card className="glass-card" title="样本结果对比">
            <Table
              rowKey="candidate_id"
              dataSource={debiasingResult?.sample_preview ?? []}
              pagination={false}
              columns={[
                { title: '候选人', dataIndex: 'candidate_id' },
                { title: '保护群体', dataIndex: 'protected_group', render: (value) => <Tag color={value ? 'orange' : 'default'}>{value ? '是' : '否'}</Tag> },
                { title: '真实合格', dataIndex: 'qualified', render: booleanTag },
                { title: '去偏前', dataIndex: 'baseline_passed', render: booleanTag },
                { title: '去偏后', dataIndex: 'debiased_passed', render: booleanTag },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}