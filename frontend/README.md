# Disability Intelligence Platform - Frontend

Next.js frontend for the Disability Intelligence Platform.

## Features

- Interactive dashboard with real-time data visualization
- GIS maps for beneficiary locations
- Severity assessment display
- Welfare recommendations
- AI-generated insights
- Responsive design with Tailwind CSS

## Tech Stack

- **Framework**: Next.js 14
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Maps**: Leaflet + React-Leaflet
- **Icons**: Lucide React

## Getting Started

### Prerequisites

- Node.js 18+
- npm or yarn

### Installation

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Start development server
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Production Build

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── public/
│   └── data/           # Generated analytics data
├── src/
│   ├── app/            # Next.js app directory
│   ├── components/     # React components
│   ├── lib/            # Utilities and API helpers
│   └── types/          # TypeScript type definitions
├── package.json
├── tailwind.config.ts
└── tsconfig.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:3001` |

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint