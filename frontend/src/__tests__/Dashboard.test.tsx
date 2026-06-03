import React from 'react';
import { createRoot } from 'react-dom/client';
import { act } from 'react-dom/test-utils';
import Dashboard from '../pages/Dashboard';

jest.mock('echarts-for-react', () => () => <div data-testid="chart" />);

jest.mock('../services/api', () => ({
  dashboardAPI: {
    getMetrics: jest.fn().mockResolvedValue({
      total_jds_audited: 1,
      total_resumes_scanned: 2,
      total_interviews_analyzed: 3,
      average_bias_score: 0.2,
      compliance_rate: 80,
      appeals_pending: 0,
      recent_alerts: [],
    }),
  },
}));

jest.mock('../stores/authStore', () => ({
  useAuthStore: (selector?: any) => {
    const state = { user: { id: 1, role: 'hr', company_id: 1 } };
    return selector ? selector(state) : state;
  },
}));

test('renders dashboard title', async () => {
  const container = document.createElement('div');
  document.body.appendChild(container);

  await act(async () => {
    createRoot(container).render(<Dashboard />);
  });

  expect(container.textContent).toContain('数据看板');
  document.body.removeChild(container);
});