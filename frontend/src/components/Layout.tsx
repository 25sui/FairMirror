import React from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import { Layout as AntLayout, Menu, Avatar, Dropdown } from 'antd';
import {
  DashboardOutlined,
  FileSearchOutlined,
  SafetyOutlined,
  AuditOutlined,
  FileProtectOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useAuthStore } from '../stores/authStore';
import { canAccessRoute } from '../authz';

const { Header, Sider, Content } = AntLayout;

const Layout: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const menuItems = [
    {
      key: '/',
      icon: <DashboardOutlined />,
      label: '数据看板',
    },
    {
      key: '/jd-audit',
      icon: <FileSearchOutlined />,
      label: 'JD审计',
    },
    {
      key: '/resume-shield',
      icon: <SafetyOutlined />,
      label: '简历防御',
    },
    {
      key: '/interview-monitor',
      icon: <AuditOutlined />,
      label: '面试监控',
    },
    {
      key: '/compliance-report',
      icon: <FileProtectOutlined />,
      label: '合规报告',
    },
  ].filter((item) => canAccessRoute(user?.role, item.key));

  const userMenuItems = [
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const handleMenuClick = (e: { key: string }) => {
    navigate(e.key);
  };

  const handleUserMenuClick = (e: { key: string }) => {
    if (e.key === 'logout') {
      logout();
      navigate('/login');
    }
  };

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <div style={{ color: 'white', fontSize: 24, fontWeight: 'bold' }}>
          FairMirror
        </div>
        <div style={{ display: 'flex', alignItems: 'center' }}>
          <span style={{ color: 'white', marginRight: 8 }}>
            {user?.username || '用户'}
          </span>
          <Dropdown
            menu={{ items: userMenuItems, onClick: handleUserMenuClick }}
            placement="bottomRight"
          >
            <Avatar icon={<UserOutlined />} style={{ cursor: 'pointer' }} />
          </Dropdown>
        </div>
      </Header>
      <AntLayout>
        <Sider width={200} style={{ background: '#fff' }}>
          <Menu
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ height: '100%', borderRight: 0 }}
          />
        </Sider>
        <Content style={{ padding: '24px', minHeight: 280 }}>
          <Outlet />
        </Content>
      </AntLayout>
    </AntLayout>
  );
};

export default Layout;
