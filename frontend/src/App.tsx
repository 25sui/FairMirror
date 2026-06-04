import { AuditOutlined, DashboardOutlined, ExperimentOutlined, FileProtectOutlined, SafetyCertificateOutlined, TeamOutlined } from '@ant-design/icons';
import { Layout, Menu, Select, Tag } from 'antd';
import type { ReactNode } from 'react';
import { useMemo, useState } from 'react';
import { AITechBarrierPage } from './pages/AITechBarrierPage';
import { CompliancePage } from './pages/CompliancePage';
import { DashboardPage } from './pages/DashboardPage';
import { InterviewMonitorPage } from './pages/InterviewMonitorPage';
import { JDAuditPage } from './pages/JDAuditPage';
import { ResumeShieldPage } from './pages/ResumeShieldPage';

const { Header, Sider, Content } = Layout;

type PageKey = 'dashboard' | 'jd' | 'resume' | 'interview' | 'ai' | 'compliance';

const pageMap: Record<PageKey, ReactNode> = {
  dashboard: <DashboardPage />,
  jd: <JDAuditPage />,
  resume: <ResumeShieldPage />,
  interview: <InterviewMonitorPage />,
  ai: <AITechBarrierPage />,
  compliance: <CompliancePage />,
};

const navItems = [
  { key: 'dashboard', icon: <DashboardOutlined />, label: '总览' },
  { key: 'jd', icon: <AuditOutlined />, label: '岗位审计' },
  { key: 'resume', icon: <FileProtectOutlined />, label: '简历检查' },
  { key: 'interview', icon: <TeamOutlined />, label: '面试监控' },
  { key: 'ai', icon: <ExperimentOutlined />, label: '算法壁垒' },
  { key: 'compliance', icon: <SafetyCertificateOutlined />, label: '合规报告' },
];

const roleOptions: { value: string; label: string; defaultPage: PageKey; pages: PageKey[] }[] = [
  { value: '企业管理员', label: '企业管理员', defaultPage: 'dashboard', pages: ['dashboard', 'jd', 'resume', 'interview', 'ai', 'compliance'] },
  { value: 'HR', label: 'HR', defaultPage: 'jd', pages: ['jd', 'interview', 'ai', 'dashboard'] },
  { value: '求职者', label: '求职者', defaultPage: 'resume', pages: ['resume'] },
  { value: '审计员', label: '审计员', defaultPage: 'compliance', pages: ['compliance', 'dashboard', 'interview', 'ai'] },
];

function App() {
  const [page, setPage] = useState<PageKey>('dashboard');
  const [role, setRole] = useState('企业管理员');
  const currentRole = roleOptions.find((item) => item.value === role) ?? roleOptions[0];
  const allowedPages = currentRole.pages;
  const visibleNavItems = navItems.filter((item) => allowedPages.includes(item.key as PageKey));
  const activePage = allowedPages.includes(page) ? page : currentRole.defaultPage;
  const activeView = useMemo(() => pageMap[activePage], [activePage]);

  const handleRoleChange = (value: string) => {
    setRole(value);
    const nextPage = roleOptions.find((item) => item.value === value)?.defaultPage;
    if (nextPage) setPage(nextPage);
  };

  return (
    <Layout className="app-shell">
      <Sider width={256} className="side-panel">
        <div className="brand-block">
          <div className="brand-mark">FM</div>
          <div>
            <h2>FairMirror</h2>
            <span>招聘公平审计</span>
          </div>
        </div>
        <Menu theme="dark" mode="inline" selectedKeys={[activePage]} items={visibleNavItems} onClick={({ key }) => setPage(key as PageKey)} />
      </Sider>
      <Layout>
        <Header className="topbar">
          <div>
            <Tag color="default">演示版</Tag>
            <span className="topbar-title">招聘公平审计平台</span>
          </div>
          <Select value={role} onChange={handleRoleChange} options={roleOptions.map(({ value, label }) => ({ value, label }))} />
        </Header>
        <Content className="content-canvas">{activeView}</Content>
      </Layout>
    </Layout>
  );
}

export default App;