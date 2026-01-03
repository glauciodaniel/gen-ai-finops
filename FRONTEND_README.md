# GenAIFinOps Frontend

Modern, dark-mode dashboard for AI cost optimization built with React, TypeScript, and Tailwind CSS.

## Features

### Dashboard
- Real-time system health monitoring
- Knowledge base statistics
- Provider overview
- Quick start guide

### Oracle (Chat Interface)
- Natural language pricing queries
- Real-time RAG-powered responses
- Suggested questions
- Chat history

### Architect (Cost Optimizer)
- Use case analysis form
- AI-powered model recommendations
- Cost comparison charts
- Annual savings calculations
- Alternative model suggestions

## Tech Stack

- **Vite** - Build tool
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Recharts** - Data visualization
- **Lucide React** - Icons

## Getting Started

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API URL

Create a `.env` file (copy from `.env.example`):

```bash
VITE_API_URL=http://localhost:8000
```

### 3. Start Backend API

In a separate terminal, start the backend:

```bash
cd gen_ai_finops
python main.py server
```

The API will run on http://localhost:8000

### 4. Start Frontend

```bash
npm run dev
```

The app will run on http://localhost:5173

## Development

### Project Structure

```
src/
├── components/
│   ├── ui/           # Design system components
│   │   ├── Card.tsx
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   └── Badge.tsx
│   └── Layout.tsx    # Main layout with sidebar
├── pages/
│   ├── Dashboard.tsx # Home page
│   ├── Oracle.tsx    # Chat interface
│   └── Architect.tsx # Cost optimizer
├── services/
│   └── api.ts        # API integration
├── types/
│   └── api.ts        # TypeScript types
├── App.tsx           # Main app with routing
└── main.tsx          # Entry point
```

### Available Scripts

```bash
npm run dev       # Start development server
npm run build     # Build for production
npm run preview   # Preview production build
npm run lint      # Run ESLint
```

## Design System

### Colors

**Dark Mode Base:**
- Background: `slate-950` to `slate-900`
- Cards: `slate-800/50` with backdrop blur
- Borders: `slate-700`

**Accent Colors:**
- Primary (Money/Savings): `emerald-500` to `emerald-600`
- Secondary (AI): `purple-600` to `blue-600`
- Success: `emerald-400`
- Info: `blue-400`
- Warning: `amber-400`

### Components

**Button Variants:**
- `primary` - Emerald gradient (main actions)
- `secondary` - Slate background (secondary actions)
- `ghost` - Transparent (subtle actions)
- `success` - Purple-Blue gradient (CTA)

**Card:**
- Semi-transparent background with backdrop blur
- Hover effects optional
- Consistent border radius (`rounded-xl`)

**Input:**
- Dark background with focus ring
- Emerald focus color
- Error state support

**Badge:**
- Multiple variants (success, info, warning, default)
- Subtle backgrounds with borders

## API Integration

All API calls are centralized in `src/services/api.ts`:

```typescript
import { api } from './services/api';

// Health check
const health = await api.health();

// Get statistics
const stats = await api.getStats();

// Ask Oracle
const response = await api.askOracle({
  question: 'What is the cheapest model?',
  n_results: 5,
});

// Optimize costs
const analysis = await api.optimizeCosts({
  use_case_description: 'Chatbot with function calling',
  monthly_input_tokens: 10000000,
  current_model: 'gpt-4',
});
```

## Features in Detail

### 1. Dashboard

**Key Metrics:**
- Total models monitored
- Number of providers
- System health status
- LLM availability

**Provider List:**
- Shows all monitored providers
- Model count per provider
- Active status badges

**Quick Start:**
- Step-by-step guide
- Links to Oracle and Architect

### 2. Oracle (Chat)

**Features:**
- Real-time chat interface
- Message history
- Suggested questions
- Loading states
- Error handling

**Example Queries:**
- "What is the cheapest GPT model?"
- "Which models support function calling?"
- "Compare GPT-4 and GPT-3.5 pricing"

### 3. Architect (Optimizer)

**Input Form:**
- Use case description (required)
- Monthly input tokens (required)
- Monthly output tokens (optional)
- Current model (optional)

**Results Display:**
- Prominent savings card (annual savings)
- Recommendation card with reasoning
- Cost comparison chart (Bar chart)
- Alternative options list
- Model features (vision, functions, context)

**Chart:**
- Recharts bar chart
- Current vs Recommended costs
- Red (current) vs Green (recommended)
- Responsive design

## Enterprise Features (Teasers)

The "Connect Cloud Account" button in the sidebar shows an alert:

```
🚀 Automated cost tracking is available in GenAIFinOps Enterprise.

Contact: enterprise@genaifinops.com
```

This demonstrates the "Open Core" strategy without implementing the feature.

## Responsive Design

- Mobile-first approach
- Sidebar collapses on mobile with hamburger menu
- Touch-friendly interactions
- Responsive grids and layouts

## Performance

- Code splitting with React.lazy (can be added)
- Optimized bundle size
- Efficient re-renders with proper state management
- Debounced API calls where appropriate

## Troubleshooting

**API Connection Issues:**
- Ensure backend is running on port 8000
- Check CORS is enabled in backend
- Verify `.env` file has correct API URL

**Build Warnings:**
- Large chunk warning is expected (Recharts library)
- Consider code splitting for production

**Type Errors:**
- Run `npm run typecheck` to verify types
- Ensure all API types match backend

## Future Enhancements

- [ ] Authentication & user accounts
- [ ] Saved optimization scenarios
- [ ] Cost alerts and notifications
- [ ] Export reports (PDF/CSV)
- [ ] Historical data & trends
- [ ] Dark/Light mode toggle
- [ ] Multi-language support
- [ ] Advanced filtering & search

## License

MIT License - See LICENSE for details.

---

**Status**: ✅ Frontend Complete - Production Ready

**Live Demo**: http://localhost:5173 (after `npm run dev`)
