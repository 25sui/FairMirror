import React, { useState, useRef } from 'react';
import { Card, Row, Col, Button, Alert, Tag, List, Spin, message, Statistic, Progress, Input, Upload, Typography } from 'antd';
import {
  AuditOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined,
  UploadOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { interviewAPI } from '../services/api';
import { InterviewAnalysisResponse, BiasLevel } from '../types';

const { TextArea } = Input;
const { Title } = Typography;

const sampleData = JSON.stringify([
  { candidate_id: 'C001', job_id: 1, scores: { technical: 4.2, communication: 3.8, problem_solving: 4.5 }, demographic_group: '男性-25-35岁' },
  { candidate_id: 'C002', job_id: 1, scores: { technical: 3.5, communication: 4.0, problem_solving: 3.2 }, demographic_group: '女性-25-35岁' },
  { candidate_id: 'C003', job_id: 1, scores: { technical: 4.0, communication: 3.5, problem_solving: 4.0 }, demographic_group: '男性-25-35岁' },
  { candidate_id: 'C004', job_id: 1, scores: { technical: 3.8, communication: 4.2, problem_solving: 3.5 }, demographic_group: '女性-25-35岁' },
  { candidate_id: 'C005', job_id: 1, scores: { technical: 4.5, communication: 4.0, problem_solving: 4.2 }, demographic_group: '男性-25-35岁' },
  { candidate_id: 'C006', job_id: 1, scores: { technical: 2.5, communication: 3.0, problem_solving: 2.8 }, demographic_group: '女性-35-45岁' },
  { candidate_id: 'C007', job_id: 1, scores: { technical: 3.2, communication: 3.5, problem_solving: 3.0 }, demographic_group: '女性-35-45岁' },
  { candidate_id: 'C008', job_id: 1, scores: { technical: 4.0, communication: 3.8, problem_solving: 4.0 }, demographic_group: '男性-35-45岁' },
], null, 2);

const InterviewMonitor: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<InterviewAnalysisResponse | null>(null);
  const [inputData, setInputData] = useState(sampleData);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleAnalyze = async () => {
    setLoading(true);
    try {
      let data;
      try {
        data = JSON.parse(inputData);
      } catch {
        message.error('请输入有效的JSON数据');
        setLoading(false);
        return;
      }

      const response = await interviewAPI.analyze(data);
      setResult(response);
      message.success('分析完成');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '分析失败');
    } finally {
      setLoading(false);
    }
  };

  const handleUseSampleData = () => {
    setInputData(sampleData);
    message.info('已加载示例数据');
  };

  const handleFileUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (event) => {
        try {
          const content = event.target?.result as string;
          JSON.parse(content);
          setInputData(content);
          message.success('文件加载成功');
        } catch {
          message.error('无效的JSON文件');
        }
      };
      reader.readAsText(file);
    }
  };

  const getRiskColor = (level: BiasLevel) => {
    switch (level) {
      case BiasLevel.HIGH:
        return '#ff4d4f';
      case BiasLevel.MEDIUM:
        return '#faad14';
      case BiasLevel.LOW:
        return '#52c41a';
      default:
        return '#888';
    }
  };

  const passRateChartOption = result ? {
    title: {
      text: '各群体通过率对比',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: Object.keys(result.fairness_metrics.group_pass_rates),
    },
    yAxis: {
      type: 'value',
      name: '通过率',
      max: 1,
    },
    series: [
      {
        name: '通过率',
        type: 'bar',
        data: Object.values(result.fairness_metrics.group_pass_rates),
        itemStyle: {
          color: (params: any) => {
            const value = params.value;
            if (value >= 0.8) return '#52c41a';
            if (value >= 0.5) return '#faad14';
            return '#ff4d4f';
          },
        },
      },
    ],
  } : {};

  return (
    <div>
      <Title level={2}>AI面试公平性监控</Title>

      <Card
        title="面试数据输入"
        style={{ marginBottom: 24 }}
      >
        <div style={{ marginBottom: 16 }}>
          <Row gutter={16}>
            <Col xs={24} sm={12}>
              <Button
                type="default"
                icon={<FileTextOutlined />}
                onClick={handleUseSampleData}
              >
                使用示例数据
              </Button>
            </Col>
            <Col xs={24} sm={12}>
              <Upload.Dragger
                beforeUpload={() => false}
                onChange={() => {}}
                onClick={() => fileInputRef.current?.click()}
              >
                <p className="ant-upload-drag-icon">
                  <UploadOutlined />
                </p>
                <p className="ant-upload-text">点击或拖拽上传JSON文件</p>
              </Upload.Dragger>
              <input
                ref={fileInputRef}
                type="file"
                accept=".json"
                onChange={handleFileUpload}
                style={{ display: 'none' }}
              />
            </Col>
          </Row>
        </div>

        <TextArea
          value={inputData}
          onChange={(e) => setInputData(e.target.value)}
          placeholder="请输入面试数据（JSON格式）"
          rows={8}
          style={{ fontFamily: 'monospace, monospace' }}
        />

        <div style={{ marginTop: 16, textAlign: 'right' }}>
          <Button
            type="primary"
            icon={<AuditOutlined />}
            onClick={handleAnalyze}
            loading={loading}
          >
            {loading ? '分析中...' : '开始分析'}
          </Button>
        </div>
      </Card>

      <Card title="分析结果">
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>正在分析面试公平性...</p>
          </div>
        ) : result ? (
          <>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="4/5法则校验"
                    value={result.fairness_metrics.four_fifths_rule_passed ? '通过' : '未通过'}
                    prefix={
                      result.fairness_metrics.four_fifths_rule_passed ? (
                        <CheckCircleOutlined style={{ color: '#52c41a' }} />
                      ) : (
                        <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
                      )
                    }
                    valueStyle={{ color: result.fairness_metrics.four_fifths_rule_passed ? '#52c41a' : '#ff4d4f' }}
                  />
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="差异影响比"
                    value={result.fairness_metrics.disparate_impact_ratio}
                    precision={3}
                    suffix={result.fairness_metrics.disparate_impact_ratio >= 0.8 ? '✓' : '✗'}
                  />
                  <div style={{ marginTop: 8, textAlign: 'center' }}>
                    {result.fairness_metrics.disparate_impact_ratio >= 0.8 ? (
                      <Tag color="success">无显著差异影响</Tag>
                    ) : (
                      <Tag color="error">存在差异影响</Tag>
                    )}
                  </div>
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <Statistic
                    title="偏见风险等级"
                    value={
                      result.fairness_metrics.bias_risk_level === BiasLevel.HIGH
                        ? '高风险'
                        : result.fairness_metrics.bias_risk_level === BiasLevel.MEDIUM
                        ? '中风险'
                        : '低风险'
                    }
                    prefix={<WarningOutlined />}
                    valueStyle={{ color: getRiskColor(result.fairness_metrics.bias_risk_level) }}
                  />
                </Card>
              </Col>
            </Row>

            <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
              <Col xs={24} lg={12}>
                <Card title="各群体通过率">
                  <ReactECharts option={passRateChartOption} style={{ height: 300 }} />
                </Card>
              </Col>
              <Col xs={24} lg={12}>
                <Card title="风险特征">
                  {result.fairness_metrics.shap_key_features.length > 0 ? (
                    <List
                      dataSource={result.fairness_metrics.shap_key_features}
                      renderItem={(feature, index) => (
                        <List.Item>
                          <Tag color="warning">{index + 1}</Tag>
                          {feature}
                        </List.Item>
                      )}
                    />
                  ) : (
                    <Alert message="未检测到明显风险特征" type="success" />
                  )}
                </Card>
              </Col>
            </Row>

            <Card title="改进建议" style={{ marginTop: 16 }}>
              <List
                dataSource={result.fairness_metrics.recommendations}
                renderItem={(rec, index) => (
                  <List.Item>
                    <Tag color="blue">{index + 1}</Tag>
                    {rec}
                  </List.Item>
                )}
              />
            </Card>
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: 60, color: '#888' }}>
            <AuditOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <p>请输入面试数据并点击"开始分析"按钮</p>
            <p>系统将分析面试数据的公平性</p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default InterviewMonitor;
