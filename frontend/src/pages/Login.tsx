import React from 'react';
import { Form, Input, Button, Card, message } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useNavigate, Link } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

const Login: React.FC = () => {
  const [loading, setLoading] = React.useState(false);
  const navigate = useNavigate();
  const { login } = useAuthStore();

  const onFinish = async (values: { email: string; password: string }) => {
    setLoading(true);
    try {
      await login(values.email, values.password);
      message.success('登录成功');
      navigate('/');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card
        title={<div style={{ textAlign: 'center', fontSize: 24 }}>FairMirror 登录</div>}
        style={{ width: 400 }}
        headStyle={{ background: 'rgba(255,255,255,0.1)', borderBottom: 0 }}
        bodyStyle={{ padding: '40px 30px' }}
      >
        <Form
          name="login"
          onFinish={onFinish}
          autoComplete="off"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[{ required: true, message: '请输入邮箱' }]}
          >
            <Input
              prefix={<UserOutlined />}
              placeholder="邮箱地址"
            />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="密码"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
              style={{ height: 45 }}
            >
              登录
            </Button>
          </Form.Item>
        </Form>

        <div style={{ textAlign: 'center', marginTop: 16 }}>
          <span style={{ color: '#888' }}>还没有账号？</span>
          <Link to="/register" style={{ marginLeft: 8 }}>
            立即注册
          </Link>
        </div>

        <div style={{ textAlign: 'center', marginTop: 24, color: '#888' }}>
          <p>FairMirror - AI反偏见招聘镜像</p>
          <p style={{ fontSize: 12 }}>推动招聘公平，让才华不被偏见辜负</p>
        </div>
      </Card>
    </div>
  );
};

export default Login;
