# TechCorp Customer Success Web App

A Next.js-based customer support portal for the TechCorp DevFlow Platform. This application provides a 24/7 AI-powered support interface with multiple contact channels.

## Features

- **Support Form**: Submit support tickets with category and priority selection
- **Ticket Tracking**: Look up and track existing support tickets
- **Documentation Portal**: Browse help articles and guides
- **About Page**: Company information and support statistics
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Dark Mode Support**: Automatic dark mode based on system preferences

## Tech Stack

- **Framework**: Next.js 14.1.0 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **UI Components**: Custom built components

## Getting Started

### Prerequisites

- Node.js 18.17 or later
- npm or yarn

### Installation

1. Clone the repository:
```bash
cd Digital_CRM_Ticket_Management_System/web-app
```

2. Install dependencies:
```bash
npm install
```

3. Copy the environment file:
```bash
cp .env.example .env.local
```

4. Update the environment variables in `.env.local`:
```env
API_BASE_URL=http://localhost:8000
OPENAI_API_KEY=your-api-key-here
```

5. Run the development server:
```bash
npm run dev
```

6. Open [http://localhost:3000](http://localhost:3000) in your browser

## Project Structure

```
web-app/
├── app/                      # Next.js App Router pages
│   ├── about/                # About page
│   ├── api/                  # API routes
│   │   └── support/
│   │       └── submit/       # Support ticket submission API
│   ├── docs/                 # Documentation page
│   ├── support/              # Support pages
│   │   ├── portal/           # Ticket tracking portal
│   │   └── page.tsx          # Support form page
│   ├── layout.tsx            # Root layout
│   └── page.tsx              # Home page
├── components/               # React components
│   ├── layout/               # Layout components
│   │   ├── Header.tsx        # Site header
│   │   └── Footer.tsx        # Site footer
│   └── ui/                   # UI components
│       ├── Badge.tsx         # Badge component
│       ├── Button.tsx        # Button component
│       ├── Card.tsx          # Card components
│       ├── Input.tsx         # Input component
│       ├── Select.tsx        # Select component
│       ├── Textarea.tsx      # Textarea component
│       └── index.ts          # Component exports
├── lib/                      # Utility functions
│   └── utils.ts              # Helper functions
├── styles/                   # Global styles
│   └── globals.css           # Tailwind CSS styles
├── types/                    # TypeScript types
│   └── index.ts              # Type definitions
├── next.config.js            # Next.js configuration
├── tailwind.config.js        # Tailwind CSS configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies
```

## Pages

### Home Page (`/`)
Landing page with product features, stats, and support channel information.

### Support Form (`/support`)
Submit a new support ticket with:
- Name and email
- Subject and category
- Priority level
- Detailed message

### Support Portal (`/support/portal`)
Track existing tickets by searching with:
- Ticket ID
- Email address
- Subject keywords

### Documentation (`/docs`)
Browse documentation by category:
- Getting Started
- Features
- Integrations
- API Reference
- Security
- Troubleshooting

### About (`/about`)
Company information, support statistics, and team details.

## API Routes

### POST `/api/support/submit`
Submit a new support ticket.

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "subject": "Issue with pipeline",
  "category": "technical",
  "priority": "high",
  "message": "Detailed description of the issue..."
}
```

**Response:**
```json
{
  "ticket_id": "TKT-ABC123-XYZ789",
  "status": "submitted",
  "message": "Your support request has been submitted successfully",
  "estimated_response_time": "15 minutes"
}
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `API_BASE_URL` | Backend API URL | `http://localhost:8000` |
| `OPENAI_API_KEY` | OpenAI API key for AI agent | (required for AI features) |
| `DATABASE_URL` | PostgreSQL connection string | (required for production) |
| `KAFKA_BROKERS` | Kafka broker addresses | (required for event streaming) |

## Integration with Backend

This frontend is designed to work with the Customer Success FTE backend:

1. **Ticket Submission**: Posts to `/api/support/submit` which forwards to the backend
2. **AI Processing**: Backend processes tickets using OpenAI Agents SDK
3. **Event Streaming**: Kafka events for real-time updates
4. **Database**: PostgreSQL for persistent storage

## Production Deployment

### Docker

```bash
docker build -t techcorp-support .
docker run -p 3000:3000 --env-file .env.local techcorp-support
```

### Kubernetes

Apply the Kubernetes manifests from the `production/k8s/` directory:

```bash
kubectl apply -f production/k8s/deployment.yaml
```

### Vercel

1. Push code to GitHub
2. Import project in Vercel
3. Configure environment variables
4. Deploy

## Contributing

1. Create a feature branch
2. Make your changes
3. Run tests and linting
4. Submit a pull request

## License

Copyright (c) 2026 TechCorp SaaS. All rights reserved.
