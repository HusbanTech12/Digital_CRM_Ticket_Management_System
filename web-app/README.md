# TechCorp Customer Success Web App

A professional, modern website built with Next.js 14 for TechCorp SaaS's DevFlow Platform.

## 🚀 Features

- **Modern UI/UX** - Built with Tailwind CSS and responsive design
- **Support Form** - Complete support ticket submission with validation
- **Documentation Hub** - Organized documentation categories
- **About Page** - Company information and team showcase
- **API Integration** - Seamless integration with backend API
- **Dark Mode Ready** - Full dark mode support
- **TypeScript** - Type-safe codebase
- **SEO Optimized** - Meta tags and semantic HTML

## 📁 Project Structure

```
web-app/
├── app/
│   ├── layout.tsx              # Root layout with Header/Footer
│   ├── page.tsx                # Home page
│   ├── support/
│   │   └── page.tsx            # Support page with form
│   ├── docs/
│   │   └── page.tsx            # Documentation page
│   ├── about/
│   │   └── page.tsx            # About page
│   └── api/
│       └── support/
│           └── route.ts        # API route for support form
├── components/
│   ├── layout/
│   │   ├── Header.tsx          # Navigation header
│   │   └── Footer.tsx          # Site footer
│   └── sections/
│       └── SupportForm.tsx     # Support form component
├── styles/
│   └── globals.css             # Global styles
├── lib/                        # Utility functions
├── public/                     # Static assets
└── package.json
```

## 🛠️ Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn
- Backend API running (for form submission)

### Installation

```bash
# Navigate to web-app directory
cd web-app

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env.local

# Edit .env.local with your API URL
# NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

### Development

```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Build for Production

```bash
# Build the application
npm run build

# Start production server
npm start
```

## 📄 Pages

### Home Page (`/`)
- Hero section with CTA
- Statistics showcase
- Features grid
- Integrations section
- CTA banner

### Support Page (`/support`)
- Support options cards (AI, Email, Live Chat)
- Complete support form with validation
- FAQ section
- Ticket ID tracking

### Documentation Page (`/docs`)
- Search functionality
- Popular topics quick links
- Documentation categories
- Help CTA section

### About Page (`/about`)
- Company story
- Statistics
- Values section
- Team showcase
- Contact information

## 🎨 Components

### Header
- Responsive navigation
- Mobile menu
- Logo and branding
- Sign in / Sign up buttons

### Footer
- Multi-column links
- Social media links
- Copyright information
- Legal links

### SupportForm
- Client-side validation
- Real-time error feedback
- Success/error states
- API integration

## 🔧 Configuration

### Tailwind Config

Custom colors configured in `tailwind.config.js`:
- `primary` - Brand colors (blue)
- `dark` - Neutral colors (slate)

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_BASE_URL` | Backend API URL (client) | `http://localhost:8000` |
| `API_BASE_URL` | Backend API URL (server) | `http://localhost:8000` |

## 🎯 Features Detail

### Form Validation
- Name: Minimum 2 characters
- Email: Valid email format
- Subject: Minimum 5 characters
- Message: Minimum 10 characters
- Category: Required selection
- Priority: Optional selection

### API Integration
- POST to `/api/support` (Next.js API route)
- Forwards to backend `/support/submit`
- Error handling with user-friendly messages
- Loading states during submission

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px)
- Mobile menu for navigation
- Grid layouts adapt to screen size

## 🚀 Deployment

### Vercel (Recommended)

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
vercel
```

### Docker

```bash
# Build Docker image
docker build -t techcorp-web .

# Run container
docker run -p 3000:3000 techcorp-web
```

### Environment Variables for Production

Set these in your hosting platform:
- `NEXT_PUBLIC_API_BASE_URL` = Your production API URL
- `API_BASE_URL` = Your production API URL (server-side)

## 📱 Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🧪 Testing

```bash
# Run tests (when configured)
npm test
```

## 📝 Code Style

- ESLint configured via Next.js
- TypeScript strict mode enabled
- Prettier for formatting (optional)

## 🔗 Related

- [Backend API Documentation](../production/README.md)
- [Hackathon Specification](../The%20CRM%20Digital%20FTE%20Factory%20Final%20Hackathon%205.md)

## 📄 License

Proprietary - TechCorp SaaS

---

**Built with Next.js 14, TypeScript, and Tailwind CSS**
