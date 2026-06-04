import { Button, Card, Col, List, Progress, Row, Space, Statistic, Table, Tag, Typography, Upload, message } from 'antd';
import type { UploadProps } from 'antd';
import { useEffect, useState } from 'react';
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { auditInterview, auditInterviewDemo } from '../services/api';
import type { InterviewAuditResponse, InterviewRecord } from '../types/audit';

const CSV_COLUMNS = ['candidate_id', 'group', 'score', 'passed', 'question_depth'];
const CSV_TEMPLATE = `${CSV_COLUMNS.join(',')}\nC001,多数群体,88,true,4\nC002,多数群体,76,true,3\nC003,保护群体,72,false,2\nC004,保护群体,69,false,1`;

function parseCsvRows(text: string): InterviewRecord[] {
  const lines = text
    .replace(/\r\n/g, '\n')
    .replace(/\r/g, '\n')
    .split('\n')
    .map((line) => line.trim())
    .filter(Boolean);

  if (lines.length < 2) {
    throw new Error('CSV 至少需要表头和一行数据');
  }

  const headers = lines[0].split(',').map((item) => item.trim());
  const missingColumns = CSV_COLUMNS.filter((column) => !headers.includes(column));
  if (missingColumns.length > 0) {
    throw new Error(`CSV 缺少列：${missingColumns.join(', ')}`);
  }

  return lines.slice(1).map((line, index) => {
    const values = line.split(',').map((item) => item.trim());
    const row = Object.fromEntries(headers.map((header, headerIndex) => [header, values[headerIndex] ?? '']));
    const score = Number(row.score);
    const questionDepth = Number(row.question_depth);
    const passed = ['true', '1', 'yes', '是', '通过'].includes(String(row.passed).toLowerCase());

    if (!row.candidate_id || !row.group || Number.isNaN(score) || Number.isNaN(questionDepth)) {
      throw new Error(`第 ${index + 2} 行数据不完整`);
    }

    return {
      candidate_id: row.candidate_id,
      group: row.group,
      score,
      passed,
      question_depth: questionDepth,
    };
  });
}

function downloadCsvTemplate() {
  const blob = new Blob([CSV_TEMPLATE], { type: 'text/csv;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'fairmirror-interview-template.csv';
  anchor.click();
  URL.revokeObjectURL(url);
}

function metricColor(status: string) {
  if (status === 'pass') return 'green';
  if (status === 'fail') return 'red';
  return 'orange';
}

function metricPercent(value: number) {
  return Math.round(Math.min(1, Math.max(0, value)) * 100);
}

export function InterviewMonitorPage() {
  const [result, setResult] = useState<InterviewAuditResponse>();
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    auditInterviewDemo().then(setResult);
  }, []);

  const uploadProps: UploadProps = {
    accept: '.csv',
    showUploadList: false,
    beforeUpload: async (file) => {
      setUploading(true);
      try {
        const text = await file.text();
        const records = parseCsvRows(text);
        const auditResult = await auditInterview(file.name.replace(/\.csv$/i, '') || '面试批次上传审计', records);
        setResult(auditResult);
        message.success(`已审计 ${records.length} 条面试记录`);
      } catch (error) {
        message.error(error instanceof Error ? error.message : 'CSV 解析失败');
      } finally {
        setUploading(false);
      }
      return false;
    },
  };

  if (!result) return <Card loading />;

  return (
    <div className="page-stack">
      <section className="hero-panel compact">
        <div>
          <Tag color={result.four_fifths_rule ? 'green' : 'red'}>{result.four_fifths_rule ? '正常' : '需复核'}</Tag>
          <h1>面试监控</h1>
          <p>{result.batch_name} · 差异影响比 {result.disparate_impact_ratio}</p>
        </div>
        <Space direction="vertical" align="end">
          <Statistic title="风险等级" value={result.risk_level} />
          <Space>
            <Button onClick={downloadCsvTemplate}>下载 CSV 模板</Button>
            <Upload {...uploadProps}>
              <Button type="primary" loading={uploading}>上传面试 CSV</Button>
            </Upload>
          </Space>
        </Space>
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
        <Col span={24}>
          <Card className="glass-card" title="公平性指标">
            <Row gutter={[14, 14]}>
              {result.fairness_metrics.map((metric) => (
                <Col xs={24} md={12} xl={8} key={metric.code}>
                  <Card size="small" title={metric.label} extra={<Tag color={metricColor(metric.status)}>{metric.status}</Tag>}>
                    <Statistic value={metric.value} precision={metric.value < 1 ? 3 : 1} />
                    <Progress percent={metricPercent(metric.value)} showInfo={false} strokeColor={metric.status === 'fail' ? '#dc2626' : '#0f766e'} />
                    <Typography.Text type="secondary">阈值：{metric.threshold}</Typography.Text>
                    <Typography.Paragraph style={{ marginTop: 8, marginBottom: 0 }}>{metric.explanation}</Typography.Paragraph>
                  </Card>
                </Col>
              ))}
            </Row>
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
        <Col span={24}>
          <Card className="glass-card" title="计算口径">
            <List
              dataSource={result.calculation_notes}
              renderItem={(item) => <List.Item>{item}</List.Item>}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
}