import React, { useState } from 'react';
import { Card, Row, Col, Input, Button, Alert, Tag, Progress, List, Spin, message } from 'antd';
import { FileSearchOutlined, ExperimentOutlined } from '@ant-design/icons';
import { jdAPI } from '../services/api';
import { JDAuditResponse, BiasLevel, BiasType } from '../types';

const { TextArea } = Input;

const JDAudit: React.FC = () => {
  const [jdText, setJdText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<JDAuditResponse | null>(null);

  const handleAnalyze = async () => {
    if (!jdText.trim()) {
      message.warning('请输入JD内容');
      return;
    }

    setLoading(true);
    try {
      const response = await jdAPI.analyze(jdText);
      setResult(response);
      message.success('分析完成');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '分析失败');
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

  const getBiasTypeLabel = (type: BiasType) => {
    const labels: Record<BiasType, string> = {
      [BiasType.GENDER]: '性别偏见',
      [BiasType.AGE]: '年龄偏见',
      [BiasType.EDUCATION]: '学历偏见',
      [BiasType.REGION]: '地域偏见',
      [BiasType.RACE]: '种族偏见',
      [BiasType.APPEARANCE]: '外貌偏见',
    };
    return labels[type] || type;
  };

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>JD智能审计官</h1>

      <Row gutter={[16, 16]}>
        <Col xs={24} lg={12}>
          <Card
            title="输入岗位描述"
            extra={<Button icon={<ExperimentOutlined />} onClick={handleAnalyze} loading={loading}>开始分析</Button>}
          >
            <TextArea
              rows={15}
              placeholder="请粘贴或输入岗位描述内容..."
              value={jdText}
              onChange={(e) => setJdText(e.target.value)}
              style={{ marginBottom: 16 }}
            />
            <div style={{ textAlign: 'center' }}>
              <Button
                type="primary"
                size="large"
                icon={<FileSearchOutlined />}
                onClick={handleAnalyze}
                loading={loading}
              >
                {loading ? '分析中...' : '开始审计'}
              </Button>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          {loading ? (
            <Card>
              <div style={{ textAlign: 'center', padding: 60 }}>
                <Spin size="large" />
                <p style={{ marginTop: 16 }}>正在分析偏见内容...</p>
              </div>
            </Card>
          ) : result ? (
            <Card title="审计结果">
              <div style={{ marginBottom: 24 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 8 }}>
                  <span style={{ fontSize: 16, fontWeight: 600 }}>总体偏见评分</span>
                  <Tag color={getLevelColor(result.overall_level)} style={{ fontSize: 16 }}>
                    {result.overall_level.toUpperCase()}
                  </Tag>
                </div>
                <Progress
                  percent={Math.round(result.overall_score * 100)}
                  strokeColor={result.overall_level === BiasLevel.HIGH ? '#ff4d4f' : result.overall_level === BiasLevel.MEDIUM ? '#faad14' : '#52c41a'}
                  format={(percent) => `${percent}%`}
                />
              </div>

              <Alert
                message="偏见检测结果"
                description={`检测到 ${result.bias_results.length} 个潜在偏见点`}
                type={result.overall_level === BiasLevel.HIGH ? 'error' : result.overall_level === BiasLevel.MEDIUM ? 'warning' : 'success'}
                style={{ marginBottom: 16 }}
              />

              <List
                header={<div style={{ fontWeight: 600 }}>详细问题列表</div>}
                dataSource={result.bias_results}
                renderItem={(item, index) => (
                  <List.Item key={index}>
                    <List.Item.Meta
                      avatar={
                        <Tag color={getLevelColor(item.level)} style={{ margin: '10px 0' }}>
                          {getBiasTypeLabel(item.type)}
                        </Tag>
                      }
                      title={
                        <div>
                          <span style={{ color: '#ff4d4f', fontWeight: 600 }}>"{item.text}"</span>
                          <Tag style={{ marginLeft: 8 }}>严重程度: {item.severity}/5</Tag>
                        </div>
                      }
                      description={
                        <div>
                          <p style={{ margin: '8px 0' }}><strong>建议:</strong> {item.suggestion}</p>
                          <p style={{ margin: 0, color: '#888' }}>
                            位置: 第{item.position[0]} - {item.position[1]}字符
                          </p>
                        </div>
                      }
                    />
                  </List.Item>
                )}
                locale={{ emptyText: '未检测到偏见' }}
              />

              {result.suggestions.length > 0 && (
                <div style={{ marginTop: 24 }}>
                  <h4>修改建议</h4>
                  <List
                    size="small"
                    dataSource={result.suggestions}
                    renderItem={(suggestion, index) => (
                      <List.Item>
                        {index + 1}. {suggestion}
                      </List.Item>
                    )}
                  />
                </div>
              )}
            </Card>
          ) : (
            <Card>
              <div style={{ textAlign: 'center', padding: 60, color: '#888' }}>
                <FileSearchOutlined style={{ fontSize: 48, marginBottom: 16 }} />
                <p>请在左侧输入岗位描述</p>
                <p>系统将自动检测其中的偏见内容</p>
              </div>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
};

export default JDAudit;
