import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Progress, List, Spin, Empty, message } from 'antd';
import {
  FileSearchOutlined,
  SafetyOutlined,
  AuditOutlined,
  CheckCircleOutlined,
  WarningOutlined,
  RiseOutlined,
} from '@ant-design/icons';
import ReactECharts from 'echarts-for-react';
import { dashboardAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { DashboardMetrics } from '../types';

const emptyMetrics: DashboardMetrics = {
  total_jds_audited: 0,
  total_resumes_scanned: 0,
  total_interviews_analyzed: 0,
  average_bias_score: 0,
  compliance_rate: 0,
  appeals_pending: 0,
  recent_alerts: [],
};

const Dashboard: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState<DashboardMetrics>(emptyMetrics);

  useEffect(() => {
    const loadMetrics = async () => {
      setLoading(true);
      try {
        const data = await dashboardAPI.getMetrics(user?.company_id);
        setMetrics(data);
      } catch (error: any) {
        message.error(error.response?.data?.detail || '看板数据加载失败');
      } finally {
        setLoading(false);
      }
    };

    loadMetrics();
  }, [user?.company_id]);

  const biasChartOption = {
    title: { text: '偏见风险概览', left: 'center' },
    tooltip: { trigger: 'axis' },
    xAxis: { type: 'category', data: ['JD审计', '简历扫描', '面试分析'] },
    yAxis: { type: 'value', name: '记录数量' },
    series: [
      {
        name: '记录数量',
        type: 'bar',
        data: [
          metrics.total_jds_audited,
          metrics.total_resumes_scanned,
          metrics.total_interviews_analyzed,
        ],
        itemStyle: { color: '#1890ff' },
      },
    ],
  };

  const complianceChartOption = {
    title: { text: '合规状态', left: 'center' },
    tooltip: { trigger: 'item' },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        data: [
          { value: metrics.compliance_rate, name: '已通过' },
          { value: Math.max(0, 100 - metrics.compliance_rate), name: '待整改' },
        ],
      },
    ],
  };

  return (
    <Spin spinning={loading}>
      <div>
        <h1 style={{ marginBottom: 24 }}>数据看板</h1>

        <Row gutter={[16, 16]}>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="已审计JD" value={metrics.total_jds_audited} prefix={<FileSearchOutlined />} valueStyle={{ color: '#1890ff' }} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="简历防御扫描" value={metrics.total_resumes_scanned} prefix={<SafetyOutlined />} valueStyle={{ color: '#52c41a' }} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="面试监控" value={metrics.total_interviews_analyzed} prefix={<AuditOutlined />} valueStyle={{ color: '#faad14' }} />
            </Card>
          </Col>
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic title="合规通过率" value={metrics.compliance_rate} suffix="%" prefix={<CheckCircleOutlined />} valueStyle={{ color: '#52c41a' }} />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="审计记录分布">
              <ReactECharts option={biasChartOption} style={{ height: 300 }} />
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="合规评分分布">
              <ReactECharts option={complianceChartOption} style={{ height: 300 }} />
            </Card>
          </Col>
        </Row>

        <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
          <Col xs={24} lg={12}>
            <Card title="平均偏见风险">
              <div style={{ padding: '0 20px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                  <span>平均偏见分</span>
                  <span>{Math.round(metrics.average_bias_score * 100)}%</span>
                </div>
                <Progress percent={Math.round(metrics.average_bias_score * 100)} strokeColor="#faad14" />
              </div>
            </Card>
          </Col>
          <Col xs={24} lg={12}>
            <Card title="最近预警">
              {metrics.recent_alerts.length === 0 ? (
                <Empty description="暂无预警" />
              ) : (
                <List
                  dataSource={metrics.recent_alerts}
                  renderItem={(item) => (
                    <List.Item>
                      <List.Item.Meta
                        avatar={
                          item.type === 'warning' ? (
                            <WarningOutlined style={{ color: '#faad14', fontSize: 20 }} />
                          ) : (
                            <RiseOutlined style={{ color: '#1890ff', fontSize: 20 }} />
                          )
                        }
                        title={item.message}
                        description={item.time}
                      />
                    </List.Item>
                  )}
                />
              )}
            </Card>
          </Col>
        </Row>
      </div>
    </Spin>
  );
};

export default Dashboard;