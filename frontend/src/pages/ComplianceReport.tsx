import React, { useState } from 'react';
import { Card, Row, Col, Button, Tabs, Table, Tag, Progress, Spin, message } from 'antd';
import { FileProtectOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { complianceAPI } from '../services/api';
import { useAuthStore } from '../stores/authStore';
import { ComplianceReport } from '../types';

const ComplianceReportPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [euReport, setEuReport] = useState<ComplianceReport | null>(null);
  const [chinaReport, setChinaReport] = useState<ComplianceReport | null>(null);
  const [activeTab, setActiveTab] = useState('eu');
  const user = useAuthStore((state) => state.user);

  const handleLoadReports = async () => {
    if (!user?.company_id) {
      message.warning('当前账号未绑定公司，无法生成合规报告');
      return;
    }
    setLoading(true);
    try {
      const companyId = user?.company_id;
      const [eu, china] = await Promise.all([
        complianceAPI.getEUAIActReport(companyId),
        complianceAPI.getChinaAIethicsReport(companyId),
      ]);
      setEuReport(eu);
      setChinaReport(china);
      message.success('报告加载成功');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '加载失败');
    } finally {
      setLoading(false);
    }
  };

  const euColumns = [
    {
      title: '检查项ID',
      dataIndex: 'item_id',
      key: 'item_id',
      width: 100,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      dataIndex: 'passed',
      key: 'passed',
      render: (passed: boolean) => (
        <Tag color={passed ? 'success' : 'error'} icon={passed ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {passed ? '通过' : '未通过'}
        </Tag>
      ),
    },
    {
      title: '详情',
      dataIndex: 'details',
      key: 'details',
      width: 300,
    },
  ];

  const chinaColumns = [
    {
      title: '检查项ID',
      dataIndex: 'item_id',
      key: 'item_id',
      width: 100,
    },
    {
      title: '描述',
      dataIndex: 'description',
      key: 'description',
    },
    {
      title: '状态',
      dataIndex: 'passed',
      key: 'passed',
      render: (passed: boolean) => (
        <Tag color={passed ? 'success' : 'error'} icon={passed ? <CheckCircleOutlined /> : <CloseCircleOutlined />}>
          {passed ? '通过' : '未通过'}
        </Tag>
      ),
    },
    {
      title: '详情',
      dataIndex: 'details',
      key: 'details',
      width: 300,
    },
  ];

  const currentReport = activeTab === 'eu' ? euReport : chinaReport;

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>合规报告</h1>

      <Card
        title="合规检查"
        extra={
          <Button
            type="primary"
            icon={<FileProtectOutlined />}
            onClick={handleLoadReports}
            loading={loading}
          >
            加载报告
          </Button>
        }
      >
        {loading ? (
          <div style={{ textAlign: 'center', padding: 60 }}>
            <Spin size="large" />
            <p style={{ marginTop: 16 }}>正在生成合规报告...</p>
          </div>
        ) : currentReport ? (
          <>
            <Row gutter={[16, 16]}>
              <Col xs={24} sm={8}>
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 48, fontWeight: 'bold', color: currentReport.overall_passed ? '#52c41a' : '#ff4d4f' }}>
                      {currentReport.compliance_score}%
                    </div>
                    <div style={{ marginTop: 8 }}>合规评分</div>
                    <Progress
                      percent={currentReport.compliance_score}
                      strokeColor={currentReport.compliance_score >= 80 ? '#52c41a' : currentReport.compliance_score >= 60 ? '#faad14' : '#ff4d4f'}
                      style={{ marginTop: 12 }}
                    />
                  </div>
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 32, fontWeight: 'bold' }}>
                      {currentReport.check_items.filter(item => item.passed).length} / {currentReport.check_items.length}
                    </div>
                    <div style={{ marginTop: 8 }}>通过检查项</div>
                    <Tag color={currentReport.overall_passed ? 'success' : 'error'} style={{ marginTop: 12 }}>
                      {currentReport.overall_passed ? '✓ 总体通过' : '✗ 总体未通过'}
                    </Tag>
                  </div>
                </Card>
              </Col>
              <Col xs={24} sm={8}>
                <Card>
                  <div style={{ textAlign: 'center' }}>
                    <div style={{ fontSize: 24, fontWeight: 'bold' }}>
                      {currentReport.regulation_type}
                    </div>
                    <div style={{ marginTop: 8 }}>法规类型</div>
                    <Tag color="blue" style={{ marginTop: 12 }}>
                      生成时间: {new Date(currentReport.generated_at).toLocaleString()}
                    </Tag>
                  </div>
                </Card>
              </Col>
            </Row>

            <Tabs
              activeKey={activeTab}
              onChange={setActiveTab}
              items={[
                {
                  key: 'eu',
                  label: 'EU AI Act',
                  children: (
                    <Table
                      dataSource={euReport?.check_items || []}
                      columns={euColumns}
                      rowKey="item_id"
                      pagination={false}
                    />
                  ),
                },
                {
                  key: 'china',
                  label: '中国AI伦理',
                  children: (
                    <Table
                      dataSource={chinaReport?.check_items || []}
                      columns={chinaColumns}
                      rowKey="item_id"
                      pagination={false}
                    />
                  ),
                },
              ]}
              style={{ marginTop: 16 }}
            />
          </>
        ) : (
          <div style={{ textAlign: 'center', padding: 60, color: '#888' }}>
            <FileProtectOutlined style={{ fontSize: 48, marginBottom: 16 }} />
            <p>点击"加载报告"按钮</p>
            <p>系统将生成EU AI Act和中国AI伦理合规报告</p>
          </div>
        )}
      </Card>
    </div>
  );
};

export default ComplianceReportPage;
