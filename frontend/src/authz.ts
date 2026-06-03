export type UserRole = 'admin' | 'hr' | 'candidate' | 'auditor';

export const ROLE_HOME: Record<UserRole, string> = {
  admin: '/',
  hr: '/',
  candidate: '/resume-shield',
  auditor: '/compliance-report',
};

export const ROUTE_ROLES: Record<string, UserRole[]> = {
  '/': ['admin', 'hr', 'auditor'],
  '/jd-audit': ['admin', 'hr'],
  '/resume-shield': ['admin', 'hr', 'candidate'],
  '/interview-monitor': ['admin', 'hr', 'auditor'],
  '/compliance-report': ['admin', 'hr', 'auditor'],
};

export const canAccessRoute = (role: string | undefined, route: string): boolean => {
  if (!role) return false;
  const allowedRoles = ROUTE_ROLES[route];
  return Boolean(allowedRoles?.includes(role as UserRole));
};

export const getRoleHome = (role: string | undefined): string => {
  if (!role) return '/login';
  return ROLE_HOME[role as UserRole] || '/';
};