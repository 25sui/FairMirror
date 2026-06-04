import { Button, Card, Col, List, Progress, Row, Space, Tag, Typography, Input, Upload, message } from 'antd';
import type { UploadProps } from 'antd';
import { useEffect, useState } from 'react';
import { EvidenceText } from '../components/EvidenceText';
import { auditResume, extractDocument, getDemo } from '../services/api';
import type { ResumeAuditResponse } from '../types/audit';

const { TextArea } = Input;

export function ResumeShieldPage() {
  const [content, setContent] = useState('');
  const [result, setResult] = useState<ResumeAuditResponse>();
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    getDemo().then((demo) => setContent(demo.resume));
  }, []);

  const uploadProps: UploadProps = {
    accept: '.txt,.md,.csv,.docx,.pdf',
    showUploadList: false,
    beforeUpload: async (file) => {
      setUploading(true);
      try {
        const parsed = await extractDocument(file);
        setContent(parsed.text);
        message.success(`已读取 ${parsed.filename ?? file.name}，共 ${parsed.characters} 字符`);
      } catch (error) {
        message.error('文件解析失败，请确认格式或改用可复制文本文件');
      } finally {
        setUploading(false);
      }
      return false;
    },
  };

  return (
    <div className="page-stack">
      <Card className="glass-card" title="简历检查" extra={<Tag color="default">求职者</Tag>}>
        <Space direction="vertical" size={12} style={{ width: '100%' }}>
          <Upload {...uploadProps}>
            <Button loading={uploading}>上传简历文件</Button>
          </Upload>
          <TextArea value={content} onChange={(event) => setContent(event.target.value)} rows={8} />
          <Button className="primary-action" type="primary" onClick={() => auditResume('张敏', content, '增长产品经理').then(setResult)}>检查简历</Button>
        </Space>
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
            <Card className="glass-card" title="证据对照">
              <Row gutter={[18, 18]}>
                <Col xs={24} lg={12}>
                  <Typography.Title level={5}>原始简历命中</Typography.Title>
                  <EvidenceText text={content} findings={result.findings} />
                </Col>
                <Col xs={24} lg={12}>
                  <Typography.Title level={5}>匿名化版本</Typography.Title>
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