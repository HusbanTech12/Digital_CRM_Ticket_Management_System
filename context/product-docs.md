# DevFlow Platform - Product Documentation

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [API Reference](#api-reference)
4. [CI/CD Pipelines](#cicd-pipelines)
5. [Project Boards](#project-boards)
6. [Integrations](#integrations)
7. [Billing & Plans](#billing--plans)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Creating Your First Project

1. Log in to your DevFlow dashboard at app.devflow.com
2. Click "New Project" in the top right corner
3. Enter project name and description
4. Choose a template (Blank, Node.js, Python, or Go)
5. Click "Create Project"

### Inviting Team Members

1. Go to Project Settings > Members
2. Click "Invite Member"
3. Enter their email address
4. Select role: Viewer, Developer, or Admin
5. Send invitation

---

## Authentication

### API Keys

API keys authenticate your requests to the DevFlow API.

**Creating an API Key:**
1. Go to Settings > API Keys
2. Click "Generate New Key"
3. Give your key a descriptive name
4. Copy the key immediately - it won't be shown again
5. Store it securely (e.g., environment variable)

**Using API Keys:**
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
     https://api.devflow.com/v1/projects
```

**Security Best Practices:**
- Never commit API keys to version control
- Rotate keys every 90 days
- Use different keys for development and production
- Revoke compromised keys immediately

### OAuth 2.0

For third-party integrations, DevFlow supports OAuth 2.0.

**Authorization Flow:**
1. Redirect user to: `https://app.devflow.com/oauth/authorize?client_id=YOUR_CLIENT_ID&redirect_uri=YOUR_REDIRECT_URI&scope=read+write`
2. User authorizes your application
3. Receive authorization code at redirect URI
4. Exchange code for access token:
```bash
curl -X POST https://api.devflow.com/oauth/token \
  -d "grant_type=authorization_code" \
  -d "code=AUTH_CODE" \
  -d "client_id=YOUR_CLIENT_ID" \
  -d "client_secret=YOUR_CLIENT_SECRET" \
  -d "redirect_uri=YOUR_REDIRECT_URI"
```

---

## API Reference

### Base URL

```
https://api.devflow.com/v1
```

### Endpoints

#### List Projects

```http
GET /projects
```

**Response:**
```json
{
  "projects": [
    {
      "id": "proj_abc123",
      "name": "My App",
      "created_at": "2024-01-15T10:30:00Z",
      "members_count": 5
    }
  ]
}
```

#### Create Project

```http
POST /projects
Content-Type: application/json

{
  "name": "New Project",
  "template": "nodejs"
}
```

#### Get Pipeline Status

```http
GET /projects/{project_id}/pipelines/{pipeline_id}
```

**Response:**
```json
{
  "id": "pipe_xyz789",
  "status": "running",
  "stage": "build",
  "started_at": "2024-01-20T14:00:00Z",
  "commit": "abc123def456"
}
```

#### Trigger Pipeline

```http
POST /projects/{project_id}/pipelines
Content-Type: application/json

{
  "branch": "main",
  "variables": {
    "DEPLOY_ENV": "production"
  }
}
```

### Rate Limits

| Plan | Requests/minute | Requests/day |
|------|-----------------|--------------|
| Starter | 60 | 1,000 |
| Professional | 300 | 50,000 |
| Enterprise | 1,000 | Unlimited |

**Rate Limit Headers:**
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1705761600
```

---

## CI/CD Pipelines

### Pipeline Configuration

Pipelines are defined in `.devflow/pipeline.yml` at your repository root.

**Example Configuration:**
```yaml
name: Main Pipeline

stages:
  - name: build
    commands:
      - npm install
      - npm run build
    artifacts:
      - dist/

  - name: test
    commands:
      - npm test
    depends_on:
      - build

  - name: deploy
    commands:
      - ./deploy.sh
    depends_on:
      - test
    environment:
      - DEPLOY_ENV=production
```

### Pipeline Statuses

| Status | Description |
|--------|-------------|
| pending | Waiting to start |
| running | Currently executing |
| success | Completed successfully |
| failed | One or more stages failed |
| canceled | Manually canceled |
| skipped | Skipped due to conditions |

### Viewing Pipeline Logs

1. Navigate to Project > Pipelines
2. Click on a pipeline run
3. Click on any stage to view logs
4. Download full logs as text file

---

## Project Boards

### Board Types

**Kanban Board:**
- Columns: Backlog, To Do, In Progress, Review, Done
- Drag-and-drop cards between columns
- WIP limits per column

**Scrum Board:**
- Sprint-based workflow
- Burndown charts
- Velocity tracking
- Sprint planning tools

### Creating Issues

1. Click "New Issue" on the board
2. Enter title and description
3. Assign to team member
4. Set priority: Low, Medium, High, Critical
5. Add labels and estimates
6. Click "Create"

### Issue States

| State | Description |
|-------|-------------|
| Open | New issue, not started |
| In Progress | Actively being worked on |
| In Review | Ready for code review |
| Blocked | Waiting on external dependency |
| Closed | Completed or rejected |

---

## Integrations

### GitHub Integration

**Setup:**
1. Go to Settings > Integrations > GitHub
2. Click "Connect GitHub"
3. Authorize DevFlow access
4. Select repositories to connect

**Features:**
- Automatic issue linking from commit messages
- Pipeline triggers on push/PR
- Status checks on pull requests

### Slack Integration

**Setup:**
1. Go to Settings > Integrations > Slack
2. Click "Add to Slack"
3. Select workspace and channels
4. Configure notifications

**Notifications:**
- Pipeline status updates
- New issue assignments
- Sprint start/end reminders

### Jira Migration

Import existing Jira projects:
1. Settings > Integrations > Jira
2. Provide Jira URL and credentials
3. Select projects to import
4. Map issue types and statuses

---

## Billing & Plans

### Plan Comparison

| Feature | Starter | Professional | Enterprise |
|---------|---------|--------------|------------|
| Users | 5 | Unlimited | Unlimited |
| Projects | 3 | Unlimited | Unlimited |
| CI/CD Minutes | 100/month | 1,000/month | Custom |
| Storage | 1 GB | 10 GB | Unlimited |
| Support | Community | Email | 24/7 Dedicated |
| SSO | ❌ | ❌ | ✅ |
| SLA | ❌ | ❌ | 99.9% |

### Payment Methods

- Credit card (Visa, MasterCard, Amex)
- PayPal
- Bank transfer (Enterprise only)
- Purchase order (Enterprise only)

### Upgrading/Downgrading

- Upgrades take effect immediately
- Downgrades take effect at next billing cycle
- Prorated credits applied for mid-cycle changes

### Refund Policy

- 30-day money-back guarantee for new subscriptions
- No refunds for partial months
- Enterprise contracts are non-refundable

---

## Troubleshooting

### Common Issues

#### "Invalid API Key" Error

**Causes:**
- Key was copied incorrectly
- Key has been revoked
- Using wrong environment (prod vs staging)

**Solution:**
1. Verify key matches exactly (no extra spaces)
2. Check key status in Settings > API Keys
3. Generate new key if needed

#### Pipeline Stuck in "Pending"

**Causes:**
- No available runners
- Repository connection lost
- Configuration syntax error

**Solution:**
1. Check runner availability in Settings > Runners
2. Verify repository is accessible
3. Validate pipeline.yml syntax

#### "Rate Limit Exceeded" Error

**Solution:**
1. Wait for rate limit to reset (check X-RateLimit-Reset header)
2. Implement exponential backoff in your code
3. Upgrade plan for higher limits

#### Authentication Timeout

**Causes:**
- Session expired (24-hour timeout)
- Browser cookies cleared
- SSO configuration issue

**Solution:**
1. Log in again
2. Enable "Remember me" for longer sessions
3. Contact admin for SSO issues

### Getting More Help

- **Documentation:** docs.devflow.com
- **Community Forum:** community.devflow.com
- **Status Page:** status.devflow.com
- **Email Support:** support@devflow.com (Pro/Enterprise)
- **Live Chat:** Available in dashboard (Enterprise)
