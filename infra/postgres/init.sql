CREATE TABLE IF NOT EXISTS organizations (
  id VARCHAR(64) PRIMARY KEY,
  name VARCHAR(160) NOT NULL
);

CREATE TABLE IF NOT EXISTS users (
  id VARCHAR(64) PRIMARY KEY,
  email VARCHAR(160) UNIQUE NOT NULL,
  role VARCHAR(48) NOT NULL,
  organization_id VARCHAR(64) REFERENCES organizations(id)
);

CREATE TABLE IF NOT EXISTS audit_jobs (
  id VARCHAR(64) PRIMARY KEY,
  kind VARCHAR(48) NOT NULL,
  status VARCHAR(32) NOT NULL DEFAULT 'completed',
  risk_score DOUBLE PRECISION NOT NULL DEFAULT 0,
  organization_id VARCHAR(64) REFERENCES organizations(id),
  payload JSONB NOT NULL DEFAULT '{}'
);

CREATE TABLE IF NOT EXISTS compliance_reports (
  id VARCHAR(64) PRIMARY KEY,
  organization_id VARCHAR(64) NOT NULL,
  readiness_score DOUBLE PRECISION NOT NULL,
  content TEXT NOT NULL
);

INSERT INTO organizations (id, name) VALUES ('org-demo', 'FairMirror Demo Corp') ON CONFLICT DO NOTHING;
INSERT INTO users (id, email, role, organization_id) VALUES
  ('u-admin', 'admin@fairmirror.ai', 'enterprise_admin', 'org-demo'),
  ('u-hr', 'hr@fairmirror.ai', 'hr', 'org-demo'),
  ('u-candidate', 'candidate@example.com', 'candidate', NULL),
  ('u-auditor', 'auditor@fairmirror.ai', 'auditor', 'org-demo')
ON CONFLICT DO NOTHING;