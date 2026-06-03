import React, { useState } from 'react';
import { Card, Row, Col, Input, Button, Alert, Tag, List, Spin, message, Table, Progress } from 'antd';
import { SafetyOutlined, RobotOutlined } from '@ant-design/icons';
import { resumeAPI } from '../services/api';
import { ResumeScanResponse, BiasLevel } from '../types';

const { TextArea } = Input;

const ResumeShield: React.FC = () => {
  const [resumeText, setResumeText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ResumeScanResponse | null>(null);

  const handleScan = async () => {
    if (!resumeText.trim()) {
      message.warning('请输入简历内容');
      return;
    }

    setLoading(true);
    try {
      const response = await resumeAPI.scan(resumeText);
      setResult(response);
      message.success('扫描完成');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '扫描失败');
    } finally {
      setLoading(false);
    }
  };

  const getLevelColor = (level: BiasLevel) => {
    switch (level) {
      case BiasLevel.HIGH:
        return 'red';
      case BiasLevel.MEDIUM:
        return 'orange';
      case BiasLevel.LOW:
        return 'green';
      default:
        return 'default';
    }
  };

  const atsColumns = [
    {
      title: 'ATS系统',
      dataIndex: 'system_name',
      key: 'system_name',
    },
    {
      title: '通过概率',
      dataIndex: 'pass_probability',
      key: 'pass_probability',
      render: (value: number) => (
        <Progress
          percent={Math.round(value * 100)}
          size="small"
          strokeColor={value >= 0.7 ? '#52c41a' : value >= 0.4 ? '#faad14' : '#ff4d4f'}
        />
      ),
    },
  ];

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>简历防御盾</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="输入简历内容"
            extra={<Button icon={<RobotOutlined />} onClick={handleScan} loading={loading}>智能扫描</Button>}
          >
            <TextArea
              rows={15}
              placeholder="请粘贴简历内容..."
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
              style={{ marginBottom: 16 }}
            />
            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<SafetyOutlined />}
                onClick={handleScan}
                loading={loading}
              >
                {loading ? '扫描中...' : '开始防御扫描'}
              </Button>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          {loading ? (
            <Card>
              <div style={{ textAlign: 'center', padding: 60 }}>
                <Spin size="large" />
                <p style={{ marginTop: 16 }}>正在扫描敏感信息...</p>
              </div>
            </Card>
          ) : result ? (
            <Card title="扫描结果">
              <Alert
                message="风险等级"
                description={
                  <div>
                    <Tag color={getLevelColor(result.overall_risk_level)} style={{ fontSize: 16 }}>
                      {result.overall_risk_level === BiasLevel.HIGH ? '高风险' : result.overall_risk_level === BiasLevel.MEDIUM ? '中风险' : '低风险'}
                    </Tag>
                    <span style={{ marginLeft: 16 }}>
                      检测到 {result.sensitive_fields.length} 个敏感字段
                    </span>
                  </div>
                }
                type={result.overall_risk_level === BiasLevel.HIGH ? 'error' : result.overall_risk_level === BiasLevel.MEDIUM ? 'warning' : 'success'}
                style={{ marginBottom: 16 }}
              />

              {result.sensitive_fields.length > 0 && (
                <>
                  <h4 style={{ marginBottom: 12 }}>敏感字段检测</h4>
                  <List
                    dataSource={result.sensitive_fields}
                    renderItem={(field, index) => (
                      <List.Item key={index}>
                        <List.Item.Meta
                          avatar={
                            <Tag color={getLevelColor(field.risk_level)}>
                              {field.risk_level === BiasLevel.HIGH ? '高风险' : field.risk_level === BiasLevel.MEDIUM ? '中风险' : '低风险'}
                            </Tag>
                          }
                          title={<strong>{field.field_name}</strong>}
                          description={
                            <div>
                              <p style={{ margin: '4px 0', color: '#888' }}>"{field.content}"</p>
                              <p style={{ margin: 0, color: '#1890ff' }}>建议: {field.suggestion}</p>
                            </div>
                          }
                        />
                      </List.Item>
                    )}
                    locale={{ emptyText: '未检测到敏感字段' }}
                  />
                </>
              )}

              <h4 style={{ marginTop: 24, marginBottom: 12 }}>ATS仿真结果</h4>
              <Table
                dataSource={result.ats_results}
                columns={atsColumns}
                rowKey="system_name"
                pagination={false}
                size="small"
              />

              {result.rewritten_resume && (
                <>
                  <h4 style={{ marginTop: 24, marginBottom: 12 }}>偏见免疫版本简历</h4>
                  <Card size="small" style={{ background: '#f6ffed', border: '1px solid #b7eb8f' }}>
                    <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>
                      {result.rewritten_resume}
                    </pre>
                  </Card>
                </>
              )}
            </Card>
          ) : (
            <Card>
              <div style={{ textAlign: 'center', padding: 60, color: '#888' }}>
                <SafetyOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>请在左侧输入简历内容</p>
                <p>系统将自动检测敏感信息并提供改写建议</p>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default ResumeShield;
