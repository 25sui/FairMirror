import React, { useState } from 'react';
import {
  Form,
  Input,
  Button,
  Card,
  Select,
  Checkbox,
  Divider,
  Typography,
  Alert,
  Space,
  Progress,
  message,
} from 'antd';
import {
  UserOutlined,
  LockOutlined,
  MailOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';

const { Title, Text } = Typography;
const { Option } = Select;

interface RegisterFormValues {
  username: string;
  email: string;
  password: string;
  confirmPassword: string;
  role: string;
  agreement: boolean;
}

const Register: React.FC = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [registerSuccess, setRegisterSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const navigate = useNavigate();

  const password = Form.useWatch('password', form);
  const [passwordStrength, setPasswordStrength] = useState(0);

  const validatePassword = (_: any, value: string) => {
    if (value && value !== password) {
      return Promise.reject(new Error('两次输入的密码不一致'));
    }
    return Promise.resolve();
  };

  const calculatePasswordStrength = (pwd: string): number => {
    if (!pwd) return 0;
    let strength = 0;
    if (pwd.length >= 8) strength += 25;
    if (/[a-z]/.test(pwd)) strength += 25;
    if (/[A-Z]/.test(pwd)) strength += 25;
    if (/[0-9]/.test(pwd)) strength += 12.5;
    if (/[^a-zA-Z0-9]/.test(pwd)) strength += 12.5;
    return Math.min(strength, 100);
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const strength = calculatePasswordStrength(e.target.value);
    setPasswordStrength(strength);
  };

  const getPasswordStrengthColor = () => {
    if (passwordStrength <= 25) return '#ff4d4f';
    if (passwordStrength <= 50) return '#faad14';
    if (passwordStrength <= 75) return '#1890ff';
    return '#52c41a';
  };

  const getPasswordStrengthText = () => {
    if (passwordStrength <= 25) return '弱';
    if (passwordStrength <= 50) return '中等';
    if (passwordStrength <= 75) return '良好';
    return '强';
  };

  const onFinish = async (values: RegisterFormValues) => {
    setLoading(true);
    setErrorMessage('');

    try {
      const registerData = {
        email: values.email,
        username: values.username,
        password: values.password,
        role: values.role,
      };

      await authAPI.register(registerData);

      setRegisterSuccess(true);
      message.success('注册成功！正在跳转登录...');

      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (error: any) {
      console.error('注册失败:', error);
      let errorMsg = '注册失败，请稍后重试';
      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        if (Array.isArray(detail) && detail.length > 0) {
          errorMsg = detail.map((e: any) => e.msg || e).join('; ');
        } else if (typeof detail === 'string') {
          errorMsg = detail;
        } else if (typeof detail === 'object' && detail.msg) {
          errorMsg = detail.msg;
        }
      }
      setErrorMessage(errorMsg);
      message.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const validateEmail = (_: any, value: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!value) {
      return Promise.reject(new Error('请输入邮箱地址'));
    }
    if (!emailRegex.test(value)) {
      return Promise.reject(new Error('请输入有效的邮箱格式'));
    }
    return Promise.resolve();
  };

  const validateUsername = (_: any, value: string) => {
    if (!value) {
      return Promise.reject(new Error('请输入用户名'));
    }
    if (value.length < 2) {
      return Promise.reject(new Error('用户名至少2个字符'));
    }
    if (value.length > 20) {
      return Promise.reject(new Error('用户名最多20个字符'));
    }
    if (!/^[a-zA-Z0-9_\u4e00-\u9fa5]+$/.test(value)) {
      return Promise.reject(new Error('用户名只能包含字母、数字、下划线和中文'));
    }
    return Promise.resolve();
  };

  if (registerSuccess) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ width: 500, textAlign: 'center' }}>
          <CheckCircleOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 24 }} />
          <Title level={2}>注册成功！</Title>
          <Text>您的账号已创建成功，即将跳转到登录页面...</Text>
          <div style={{ marginTop: 24 }}>
            <Button type="primary" onClick={() => navigate('/login')}>
              立即登录
            </Button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '20px 0'
    }}>
      <Card
        style={{ width: 600, maxHeight: '90vh', overflow: 'auto' }}
        headStyle={{ background: 'rgba(255,255,255,0.1)', borderBottom: 0, textAlign: 'center' }}
      >
        <div style={{ marginBottom: 24 }}>
          <Title level={2} style={{ color: '#1890ff', marginBottom: 8 }}>FairMirror 注册</Title>
          <Text type="secondary">创建账号，开启公平招聘之旅</Text>
        </div>

        {errorMessage && (
          <Alert
            message="注册失败"
            description={errorMessage}
            type="error"
            showIcon
            style={{ marginBottom: 24 }}
            closable
            onClose={() => setErrorMessage('')}
          />
        )}

        <Form
          form={form}
          name="register"
          onFinish={onFinish}
          autoComplete="off"
          layout="vertical"
          size="middle"
        >
          <Divider orientation="left">基本信息</Divider>

          <Form.Item
            label="用户名"
            name="username"
            rules={[{ required: true, validator: validateUsername }]}
            validateTrigger="onBlur"
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="请输入用户名（2-20个字符）"
              maxLength={20}
            />
          </Form.Item>

          <Form.Item
            label="邮箱地址"
            name="email"
            rules={[{ required: true, validator: validateEmail }]}
            validateTrigger="onBlur"
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="请输入有效的邮箱地址"
            />
          </Form.Item>

          <Form.Item
            label="账号类型"
            name="role"
            rules={[{ required: true, message: '请选择账号类型' }]}
            initialValue="hr"
          >
            <Select placeholder="请选择您的角色">
              <Option value="hr">企业HR</Option>
              <Option value="candidate">求职者</Option>
              <Option value="admin">管理员</Option>
              <Option value="auditor">审计员</Option>
            </Select>
          </Form.Item>

          <Divider orientation="left">安全设置</Divider>

          <Form.Item
            label="密码"
            name="password"
            rules={[
              { required: true, message: '请输入密码' },
              { min: 8, message: '密码至少8个字符' },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入密码"
              onChange={handlePasswordChange}
            />
          </Form.Item>

          {password && (
            <div style={{ marginBottom: 24 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                <Text type="secondary">密码强度</Text>
                <Text style={{ color: getPasswordStrengthColor() }}>{getPasswordStrengthText()}</Text>
              </div>
              <Progress
                percent={passwordStrength}
                showInfo={false}
                strokeColor={getPasswordStrengthColor()}
                size="small"
              />
              <div style={{ marginTop: 8, fontSize: 12, color: '#888' }}>
                <div>密码要求：</div>
                <ul style={{ paddingLeft: 20, margin: 0 }}>
                  <li style={{ color: password?.length >= 8 ? '#52c41a' : '#888' }}>
                    至少8个字符
                    {password?.length >= 8 && <CheckCircleOutlined style={{ marginLeft: 4, color: '#52c41a' }} />}
                  </li>
                  <li style={{ color: /[a-z]/.test(password || '') ? '#52c41a' : '#888' }}>
                    包含小写字母
                    {/[a-z]/.test(password || '') && <CheckCircleOutlined style={{ marginLeft: 4, color: '#52c41a' }} />}
                  </li>
                  <li style={{ color: /[A-Z]/.test(password || '') ? '#52c41a' : '#888' }}>
                    包含大写字母
                    {/[A-Z]/.test(password || '') && <CheckCircleOutlined style={{ marginLeft: 4, color: '#52c41a' }} />}
                  </li>
                  <li style={{ color: /[0-9]/.test(password || '') ? '#52c41a' : '#888' }}>
                    包含数字
                    {/[0-9]/.test(password || '') && <CheckCircleOutlined style={{ marginLeft: 4, color: '#52c41a' }} />}
                  </li>
                  <li style={{ color: /[^a-zA-Z0-9]/.test(password || '') ? '#52c41a' : '#888' }}>
                    包含特殊字符
                    {/[^a-zA-Z0-9]/.test(password || '') && <CheckCircleOutlined style={{ marginLeft: 4, color: '#52c41a' }} />}
                  </li>
                </ul>
              </div>
            </div>
          )}

          <Form.Item
            label="确认密码"
            name="confirmPassword"
            dependencies={['password']}
            rules={[
              { required: true, message: '请再次输入密码' },
              { validator: validatePassword },
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请再次输入密码"
            />
          </Form.Item>

          <Divider orientation="left">服务条款</Divider>

          <Form.Item
            name="agreement"
            valuePropName="checked"
            rules={[
              {
                validator: (_, value) =>
                  value ? Promise.resolve() : Promise.reject(new Error('请同意服务条款')),
              },
            ]}
          >
            <Checkbox>
              我已阅读并同意 <a href="#">《用户服务协议》</a> 和 <a href="#">《隐私政策》</a>
            </Checkbox>
          </Form.Item>

          <Form.Item style={{ marginBottom: 24 }}>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              size="large"
              style={{ height: 50 }}
              disabled={passwordStrength < 50}
            >
              {loading ? '注册中...' : '立即注册'}
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center', marginTop: 16 }}>
            <Text type="secondary">已有账号？</Text>
            <Link to="/login" style={{ marginLeft: 8 }}>
              立即登录
            </Link>
          </div>
        </Form>

        <Divider />

        <div style={{ textAlign: 'center', color: '#888', fontSize: 12 }}>
          <p style={{ marginBottom: 4 }}>FairMirror - AI反偏见招聘镜像</p>
          <p>推动招聘公平，让才华不被偏见辜负</p>
        </div>
      </Card>
    </div>
  );
};

export default Register;
