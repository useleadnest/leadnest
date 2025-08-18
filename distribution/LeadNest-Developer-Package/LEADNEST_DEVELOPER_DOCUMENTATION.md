# LeadNest Developer Documentation 🚀

**Version:** 2.0.0  
**Last Updated:** August 17, 2025  
**Environment:** Production Ready

---

## Table of Contents
1. [Quick Start](#quick-start)
2. [Architecture Overview](#architecture-overview)
3. [API Reference](#api-reference)
4. [Frontend Integration](#frontend-integration)
5. [Backend Services](#backend-services)
6. [Authentication & Security](#authentication--security)
7. [Production Setup](#production-setup)
8. [Testing Guide](#testing-guide)
9. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+ (production) or SQLite (development)
- Redis 6+ (for background jobs)

### 1-Minute Setup
```bash
# Clone repository
git clone https://github.com/useleadnest/leadnest.git
cd leadnest

# Windows Setup
.\setup.bat

# Linux/Mac Setup
./setup.sh

# Verify installation
curl http://localhost:5000/healthz
```

### Environment Variables
```env
# Core Configuration
DATABASE_URL=postgresql://user:pass@localhost/leadnest
JWT_SECRET=your-256-bit-secret-key
PUBLIC_BASE_URL=https://api.leadnest.com

# AI & Analytics
OPENAI_API_KEY=sk-your-openai-key
GROQ_API_KEY=your-groq-api-key

# Communication
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token

# Payments
STRIPE_SECRET_KEY=sk_live_your-stripe-key
STRIPE_WEBHOOK_SECRET=whsec_your-webhook-secret

# External APIs
YELP_API_KEY=your-yelp-api-key
REDIS_URL=redis://localhost:6379/0

# Monitoring
SENTRY_DSN=your-sentry-dsn
```

---

## Architecture Overview

### System Architecture
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React SPA     │    │   Flask API     │    │   PostgreSQL    │
│   (Vercel)      │◄──►│   (Render)      │◄──►│   (Database)    │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       ▼                       │
         │              ┌─────────────────┐              │
         └─────────────►│     Redis       │◄─────────────┘
                        │  (Job Queue)    │
                        └─────────────────┘
```

### Tech Stack
**Backend:**
- **Framework:** Flask 3.0 with Gunicorn
- **Database:** PostgreSQL with SQLAlchemy ORM
- **Cache:** Redis for sessions and job queuing
- **Background Jobs:** RQ (Redis Queue)
- **Authentication:** JWT with Flask-JWT-Extended
- **Validation:** Marshmallow schemas
- **Security:** Rate limiting, CORS, input sanitization

**Frontend:**
- **Framework:** React 18 with TypeScript
- **Build Tool:** Vite for fast development
- **Styling:** Tailwind CSS with shadcn/ui components
- **State Management:** React Context + hooks
- **HTTP Client:** Axios with interceptors
- **Routing:** React Router v6

**Infrastructure:**
- **Backend Hosting:** Render.com with auto-scaling
- **Frontend CDN:** Vercel with edge functions
- **Database:** Render PostgreSQL with backups
- **Monitoring:** Sentry for error tracking
- **CI/CD:** GitHub Actions with automated testing

---

## API Reference

### Base URL
- **Development:** `http://localhost:5000`
- **Production:** `https://api.leadnest.com`

### Authentication
All authenticated endpoints require JWT token in header:
```http
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### Core Endpoints

#### Authentication
```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "SecurePass123!",
  "business_name": "Elite Med Spa"
}

Response (201):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "email": "user@company.com",
    "business_name": "Elite Med Spa",
    "trial_expires": "2025-08-24T00:00:00Z"
  }
}
```

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@company.com",
  "password": "SecurePass123!"
}

Response (200):
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_123",
    "email": "user@company.com",
    "business_name": "Elite Med Spa"
  }
}
```

#### Lead Management
```http
GET /leads?page=1&per_page=20&search=john&status=new
Authorization: Bearer TOKEN

Response (200):
{
  "leads": [
    {
      "id": "lead_123",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+15551234567",
      "business_name": "Doe Enterprises",
      "status": "new",
      "source": "yelp_scraping",
      "created_at": "2025-08-17T10:00:00Z"
    }
  ],
  "total_count": 1,
  "page": 1,
  "per_page": 20
}
```

```http
POST /leads/bulk-import
Authorization: Bearer TOKEN
Content-Type: multipart/form-data

file: leads.csv (CSV file with headers: name,email,phone,business_name,notes)

Response (202):
{
  "job_id": "job_abc123",
  "message": "Bulk import started",
  "estimated_completion": "2025-08-17T10:05:00Z"
}
```

```http
GET /leads/import-status/job_abc123
Authorization: Bearer TOKEN

Response (200):
{
  "status": "completed",
  "processed": 150,
  "successful": 147,
  "failed": 3,
  "errors": [
    {"row": 45, "error": "Invalid email format"},
    {"row": 78, "error": "Missing required field: name"}
  ]
}
```

#### Competitive Features

##### AI Lead Scoring
```http
POST /api/ai/bulk-score-leads
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "leads": [
    {
      "id": "lead_123",
      "name": "John Doe",
      "email": "john@example.com",
      "phone": "+15551234567",
      "source": "google_ads",
      "industry": "medspas"
    }
  ]
}

Response (200):
{
  "scored_leads": [
    {
      "lead_id": "lead_123",
      "score": 85,
      "grade": "A",
      "confidence": 0.92,
      "factors": ["High-value source", "Industry match", "Complete profile"]
    }
  ],
  "stats": {
    "total_leads": 1,
    "avg_score": 85.0,
    "grade_distribution": {"A": 1, "B": 0, "C": 0},
    "high_value_count": 1
  }
}
```

##### ROI Analytics
```http
GET /api/analytics/roi?days=30&industry=medspas
Authorization: Bearer TOKEN

Response (200):
{
  "metrics": {
    "leads_uploaded": 150,
    "calls_made": 320,
    "emails_sent": 450,
    "appointments_booked": 45,
    "deals_closed": 12,
    "revenue_generated": 48000,
    "cost_per_lead": 25.50,
    "conversion_rate": 8.0,
    "roi_percentage": 275.5
  },
  "insights": [
    "Your ROI is 175% above industry average",
    "Email follow-up is driving 65% of conversions"
  ],
  "recommendations": [
    {
      "category": "conversion",
      "title": "Optimize Call Timing",
      "description": "Focus calls between 10AM-2PM for 23% higher connection rates",
      "impact": "High",
      "effort": "Low"
    }
  ]
}
```

##### Nurture Sequences
```http
POST /api/nurture/start-sequence
Authorization: Bearer TOKEN
Content-Type: application/json

{
  "lead_id": "lead_123",
  "template_id": "medspa_initial",
  "lead_data": {
    "first_name": "John",
    "service_interest": "Botox consultation"
  },
  "business_data": {
    "business_name": "Elite Med Spa",
    "agent_name": "Sarah Johnson"
  }
}

Response (200):
{
  "sequence_id": "seq_abc123",
  "total_steps": 3,
  "scheduled_steps": [
    {
      "step": 1,
      "type": "email",
      "scheduled_at": "2025-08-17T14:00:00Z",
      "subject": "Thank you for your interest, John!"
    }
  ]
}
```

##### Shared Inbox
```http
GET /api/inbox?status=unread&page=1&per_page=20
Authorization: Bearer TOKEN

Response (200):
{
  "conversations": [
    {
      "id": "conv_123",
      "lead_id": "lead_456",
      "lead_name": "John Doe",
      "subject": "Follow-up on consultation",
      "last_message": "I'm interested in scheduling next week",
      "status": "unread",
      "priority": "high",
      "assigned_to": "sarah@example.com",
      "last_activity": "2025-08-17T14:30:00Z",
      "message_count": 3
    }
  ],
  "total_count": 15,
  "page": 1,
  "per_page": 20
}
```

### Error Handling
All API endpoints return consistent error formats:

```http
HTTP/1.1 400 Bad Request
Content-Type: application/json

{
  "error": "validation_failed",
  "message": "Invalid input data",
  "details": {
    "email": ["Invalid email format"],
    "phone": ["Phone number is required"]
  },
  "timestamp": "2025-08-17T10:00:00Z",
  "request_id": "req_abc123"
}
```

**Common Status Codes:**
- `200` - Success
- `201` - Created
- `400` - Bad Request (validation errors)
- `401` - Unauthorized (invalid/missing token)
- `403` - Forbidden (insufficient permissions)
- `404` - Not Found
- `422` - Unprocessable Entity (business logic error)
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error

---

## Frontend Integration

### React/TypeScript Examples

#### API Client Setup
```typescript
// src/lib/api.ts
import axios, { AxiosInstance } from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

class LeadNestAPI {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 10000,
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = localStorage.getItem('leadnest_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('leadnest_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Auth methods
  async login(email: string, password: string) {
    const response = await this.client.post('/auth/login', { email, password });
    const { token } = response.data;
    localStorage.setItem('leadnest_token', token);
    return response.data;
  }

  async register(email: string, password: string, businessName: string) {
    const response = await this.client.post('/auth/register', {
      email,
      password,
      business_name: businessName,
    });
    const { token } = response.data;
    localStorage.setItem('leadnest_token', token);
    return response.data;
  }

  // Lead methods
  async getLeads(params = {}) {
    const response = await this.client.get('/leads', { params });
    return response.data;
  }

  async bulkImportLeads(file: File) {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/leads/bulk-import', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // AI Scoring methods
  async bulkScoreLeads(leads: any[]) {
    const response = await this.client.post('/api/ai/bulk-score-leads', { leads });
    return response.data;
  }

  async getScoredLeads(params = {}) {
    const response = await this.client.get('/api/ai/scored-leads', { params });
    return response.data;
  }

  // ROI Analytics methods
  async getROIMetrics(params = {}) {
    const response = await this.client.get('/api/analytics/roi', { params });
    return response.data;
  }
}

export const api = new LeadNestAPI();
```

#### React Hook for Lead Management
```typescript
// src/hooks/useLeads.ts
import { useState, useEffect } from 'react';
import { api } from '../lib/api';

interface Lead {
  id: string;
  name: string;
  email: string;
  phone: string;
  business_name: string;
  status: string;
  created_at: string;
}

interface LeadsState {
  leads: Lead[];
  loading: boolean;
  error: string | null;
  totalCount: number;
  page: number;
  perPage: number;
}

export const useLeads = (initialParams = {}) => {
  const [state, setState] = useState<LeadsState>({
    leads: [],
    loading: false,
    error: null,
    totalCount: 0,
    page: 1,
    perPage: 20,
  });

  const loadLeads = async (params = {}) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const data = await api.getLeads({ ...initialParams, ...params });
      
      setState(prev => ({
        ...prev,
        leads: data.leads,
        totalCount: data.total_count,
        page: data.page,
        perPage: data.per_page,
        loading: false,
      }));
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.message || 'Failed to load leads',
      }));
    }
  };

  const bulkImport = async (file: File) => {
    try {
      setState(prev => ({ ...prev, loading: true, error: null }));
      
      const result = await api.bulkImportLeads(file);
      
      // Refresh leads after import
      setTimeout(() => loadLeads(), 2000);
      
      return result;
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: error.response?.data?.message || 'Failed to import leads',
      }));
      throw error;
    }
  };

  useEffect(() => {
    loadLeads();
  }, []);

  return {
    ...state,
    loadLeads,
    bulkImport,
    refresh: () => loadLeads(),
  };
};
```

#### AI Lead Scoring Component
```typescript
// src/components/AILeadScoring.tsx
import React, { useState } from 'react';
import { api } from '../lib/api';

interface ScoredLead {
  lead_id: string;
  score: number;
  grade: string;
  confidence: number;
  factors: string[];
}

export const AILeadScoring: React.FC = () => {
  const [selectedLeads, setSelectedLeads] = useState<any[]>([]);
  const [scoredLeads, setScoredLeads] = useState<ScoredLead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleBulkScoring = async () => {
    if (selectedLeads.length === 0) {
      setError('Please select leads to score');
      return;
    }

    try {
      setLoading(true);
      setError(null);
      
      const response = await api.bulkScoreLeads(selectedLeads);
      
      setScoredLeads(response.scored_leads);
      setSelectedLeads([]);
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to score leads');
    } finally {
      setLoading(false);
    }
  };

  const getGradeColor = (grade: string) => {
    switch (grade) {
      case 'A': return 'text-green-600 bg-green-100';
      case 'B': return 'text-blue-600 bg-blue-100';
      case 'C': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">
          AI Lead Scoring
        </h2>
        
        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <button
          onClick={handleBulkScoring}
          disabled={loading || selectedLeads.length === 0}
          className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white font-bold py-2 px-4 rounded"
        >
          {loading ? 'Scoring...' : `Score ${selectedLeads.length} Leads`}
        </button>
      </div>

      {scoredLeads.length > 0 && (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Lead
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Grade
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Key Factors
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {scoredLeads.map((lead) => (
                <tr key={lead.lead_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                    {lead.lead_id}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {lead.score}/100
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getGradeColor(lead.grade)}`}>
                      {lead.grade}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {lead.factors.slice(0, 2).join(', ')}
                    {lead.factors.length > 2 && '...'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
```

---

## Backend Services

### Python Flask Service Integration

#### Service Initialization
```python
# backend-flask/app/__init__.py
from flask import Flask
from services.ai_lead_scorer import AILeadScorer
from services.roi_calculator import ROICalculator
from services.nurture_sequences import SequenceManager

def create_app():
    app = Flask(__name__)
    
    # Initialize competitive services
    app.ai_scorer = AILeadScorer()
    app.roi_calculator = ROICalculator()
    app.sequence_manager = SequenceManager()
    
    return app
```

#### Custom Service Usage
```python
# backend-flask/services/custom_service.py
import logging
from datetime import datetime
from typing import Dict, List, Optional

log = logging.getLogger(__name__)

class CustomLeadService:
    def __init__(self):
        self.ai_scorer = AILeadScorer()
        self.roi_calculator = ROICalculator()
    
    def process_lead_batch(self, leads: List[Dict]) -> Dict:
        """Process a batch of leads with scoring and ROI analysis"""
        try:
            log.info(f"Processing batch of {len(leads)} leads")
            
            # Score leads using AI
            scoring_results = self.ai_scorer.bulk_score_leads(leads)
            
            # Calculate ROI impact
            roi_impact = self.roi_calculator.estimate_lead_value(
                scored_leads=scoring_results['scored_leads']
            )
            
            return {
                'processed_count': len(leads),
                'scoring_results': scoring_results,
                'roi_impact': roi_impact,
                'processed_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log.error(f"Error processing lead batch: {e}")
            raise
    
    def generate_lead_report(self, user_id: str, days: int = 30) -> Dict:
        """Generate comprehensive lead performance report"""
        try:
            # Get ROI metrics
            roi_data = self.roi_calculator.calculate_roi_metrics(
                user_id=user_id,
                days=days
            )
            
            # Get competitive analysis
            competitive_data = self.roi_calculator.get_competitive_analysis(
                user_id=user_id,
                industry=roi_data.get('industry')
            )
            
            return {
                'user_id': user_id,
                'timeframe_days': days,
                'roi_metrics': roi_data,
                'competitive_position': competitive_data,
                'generated_at': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            log.error(f"Error generating lead report: {e}")
            raise

# Usage in API endpoints
service = CustomLeadService()

@api.route('/custom/process-leads', methods=['POST'])
@require_auth
def process_leads():
    try:
        data = request.get_json()
        leads = data.get('leads', [])
        
        result = service.process_lead_batch(leads)
        
        return jsonify(result), 200
        
    except Exception as e:
        log.error(f"Error in process_leads endpoint: {e}")
        return jsonify({'error': 'Processing failed'}), 500
```

---

## Authentication & Security

### JWT Implementation
```python
# backend-flask/app/auth.py
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
import logging

log = logging.getLogger(__name__)

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            verify_jwt_in_request()
            return f(*args, **kwargs)
        except Exception as e:
            log.warning(f"Authentication failed: {e}")
            return jsonify({'error': 'Authentication required'}), 401
    return decorated

def get_current_user_id():
    """Get the current authenticated user ID"""
    return get_jwt_identity()
```

### Rate Limiting Configuration
```python
# backend-flask/app/__init__.py
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="redis://localhost:6379"
)

# Apply to specific endpoints
@api.route('/auth/login', methods=['POST'])
@limiter.limit("5 per minute")
def login():
    pass

@api.route('/leads/export', methods=['GET'])
@limiter.limit("3 per minute")
def export_leads():
    pass
```

### Input Validation Schemas
```python
# backend-flask/app/schemas.py
from marshmallow import Schema, fields, validate, ValidationError

class LeadImportSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=2, max=100))
    email = fields.Email(required=True)
    phone = fields.Str(validate=validate.Regexp(r'^\+?[1-9]\d{10,14}$'))
    business_name = fields.Str(validate=validate.Length(max=200))
    notes = fields.Str(validate=validate.Length(max=1000))

class AIScoreRequestSchema(Schema):
    leads = fields.List(fields.Dict(), required=True, validate=validate.Length(min=1, max=100))

# Usage in endpoints
@api.route('/leads/bulk-import', methods=['POST'])
@require_auth
def bulk_import_leads():
    try:
        # Validate uploaded CSV data
        schema = LeadImportSchema(many=True)
        leads_data = schema.load(csv_data)  # Raises ValidationError if invalid
        
        # Process valid data
        job = enqueue_bulk_import(leads_data, user_id=get_current_user_id())
        
        return jsonify({'job_id': job.id}), 202
        
    except ValidationError as e:
        return jsonify({'error': 'validation_failed', 'details': e.messages}), 400
```

---

## Production Setup

### Docker Configuration
```dockerfile
# Dockerfile (backend)
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "wsgi:app"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build: ./backend-flask
    ports:
      - "5000:5000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/leadnest
      - REDIS_URL=redis://redis:6379/0
      - JWT_SECRET=${JWT_SECRET}
    depends_on:
      - db
      - redis

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000

  db:
    image: postgres:14
    environment:
      - POSTGRES_DB=leadnest
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

### Database Migrations
```python
# backend-flask/migrations/versions/001_competitive_features.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Lead scores table
    op.create_table('lead_scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('lead_id', sa.String(255), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column('grade', sa.String(2), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('factors', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_lead_scores_lead_id', 'lead_id'),
        sa.Index('ix_lead_scores_score', 'score')
    )

    # Nurture sequences table
    op.create_table('nurture_sequences',
        sa.Column('id', sa.String(255), nullable=False),
        sa.Column('lead_id', sa.String(255), nullable=False),
        sa.Column('template_id', sa.String(255), nullable=False),
        sa.Column('status', sa.String(50), nullable=False),
        sa.Column('current_step', sa.Integer(), nullable=False),
        sa.Column('scheduled_steps', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_nurture_sequences_lead_id', 'lead_id'),
        sa.Index('ix_nurture_sequences_status', 'status')
    )

def downgrade():
    op.drop_table('nurture_sequences')
    op.drop_table('lead_scores')
```

### Production Deployment Checklist
- [ ] Environment variables configured
- [ ] Database migrations applied
- [ ] Redis server running
- [ ] SSL certificates installed
- [ ] Domain DNS configured
- [ ] Monitoring (Sentry) configured
- [ ] Backup strategy implemented
- [ ] Rate limiting enabled
- [ ] Security headers configured
- [ ] CORS properly configured

---

## Testing Guide

### Running Tests
```bash
# Backend tests
cd backend-flask
python -m pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test

# End-to-end tests
npm run test:e2e
```

### Test Configuration
```python
# backend-flask/tests/conftest.py
import pytest
from app import create_app
from app.db import db

@pytest.fixture
def app():
    app = create_app({
        'TESTING': True,
        'DATABASE_URL': 'sqlite:///:memory:',
        'JWT_SECRET': 'test-secret'
    })
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client):
    # Create test user and get auth token
    response = client.post('/auth/register', json={
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'business_name': 'Test Business'
    })
    token = response.get_json()['token']
    return {'Authorization': f'Bearer {token}'}
```

### Sample Tests
```python
# backend-flask/tests/test_ai_scoring.py
def test_bulk_score_leads(client, auth_headers):
    leads_data = {
        'leads': [
            {
                'id': 'lead_1',
                'name': 'John Doe',
                'email': 'john@example.com',
                'source': 'google_ads',
                'industry': 'medspas'
            }
        ]
    }
    
    response = client.post('/api/ai/bulk-score-leads', 
                         json=leads_data, 
                         headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'scored_leads' in data
    assert len(data['scored_leads']) == 1
    assert data['scored_leads'][0]['score'] > 0

def test_bulk_score_leads_validation(client, auth_headers):
    # Test with invalid data
    response = client.post('/api/ai/bulk-score-leads', 
                         json={'leads': []}, 
                         headers=auth_headers)
    
    assert response.status_code == 400
    assert 'validation_failed' in response.get_json()['error']
```

---

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors
```bash
# Check PostgreSQL connection
psql -h localhost -U postgres -d leadnest -c "SELECT version();"

# Reset database (development only)
flask db downgrade base
flask db upgrade
```

#### 2. Redis Connection Issues
```bash
# Test Redis connection
redis-cli ping

# Check Redis logs
docker logs leadnest-redis
```

#### 3. JWT Token Issues
```python
# Debug token in Python
from flask_jwt_extended import decode_token
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
decoded = decode_token(token)
print(decoded)
```

#### 4. API Rate Limiting
```bash
# Reset rate limits (Redis)
redis-cli flushdb

# Check rate limit status
curl -I http://localhost:5000/leads
# Look for X-RateLimit-* headers
```

#### 5. CORS Issues
```javascript
// Check browser console for CORS errors
// Verify frontend API_URL matches backend URL
console.log('API URL:', process.env.REACT_APP_API_URL);
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Or in Flask app
app.config['DEBUG'] = True
app.config['TESTING'] = True
```

### Performance Monitoring
```python
# Add request timing middleware
from time import time
from flask import g, request

@app.before_request
def before_request():
    g.start_time = time()

@app.after_request
def after_request(response):
    total_time = time() - g.start_time
    if total_time > 1.0:  # Log slow requests
        app.logger.warning(f'Slow request: {request.path} took {total_time:.2f}s')
    return response
```

---

## Support & Resources

### Documentation
- **API Documentation:** `/api/docs` (Swagger UI)
- **GitHub Repository:** https://github.com/useleadnest/leadnest
- **Change Log:** https://github.com/useleadnest/leadnest/releases

### Support Channels
- **Email:** dev-support@leadnest.com
- **Discord:** https://discord.gg/leadnest-dev
- **GitHub Issues:** https://github.com/useleadnest/leadnest/issues

### Monitoring
- **Status Page:** https://status.leadnest.com
- **Performance Metrics:** https://metrics.leadnest.com
- **Error Tracking:** Sentry dashboard

---

**© 2025 LeadNest. All rights reserved.**
