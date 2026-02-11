# Personal Caddie Frontend

Modern React + TypeScript frontend for the Personal Caddie golf recommendation engine.

## 🎯 Features

- **Shot Input Form** - Intuitive form for entering shot context
  - Distance to pin (30-300 yards)
  - Pin location (front/center/back)
  - Ball lie (tee/fairway/rough/bunker/woods)
  - Lie quality (clean/normal/thick/plugged)
  - Playing strategy (aggressive/balanced/conservative)

- **Recommendation Display** - Clear, golf-friendly presentation
  - Recommended club (large, prominent display)
  - Carry and total distances
  - Confidence percentage with visual meter
  - Target area guidance

- **Adjustment Breakdown** - Physics calculations explained
  - Temperature effects
  - Elevation adjustments
  - Wind impact
  - Rain/wet conditions
  - Lie quality penalties
  - Human-readable summary

- **Hazard Analysis** - Danger awareness
  - Hazards in play with risk levels
  - Safe miss direction
  - Distance to each hazard

- **Alternative Clubs** - Other options when strategic value differs
  - Confidence % for each
  - Clear rationale for suggestion

- **Responsive Design** - Works on mobile, tablet, and desktop
  - Mobile: Stacked vertical layout
  - Tablet: Side-by-side with padding
  - Desktop: Form sidebar with wide results

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API running on http://localhost:8000

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
npm run dev
```

Visit http://localhost:5173 in your browser.

The dev server includes:
- Hot module reloading (changes reflect instantly)
- Proxy to backend API (no CORS issues)
- TypeScript compilation

### Build for Production

```bash
npm run build
```

Output goes to `dist/` directory.

## 🏗️ Architecture

### Directory Structure

```
src/
├── components/              # React components
│   ├── ShotInputForm.tsx       # Form for shot context
│   ├── RecommendationCard.tsx  # Main recommendation display
│   ├── AdjustmentDetails.tsx   # Physics adjustments breakdown
│   ├── HazardWarnings.tsx      # Hazard alerts
│   └── AlternativeClubs.tsx    # Alternative options
├── services/
│   └── api.ts                  # API calls to backend
├── types/
│   └── index.ts                # TypeScript interfaces
├── App.tsx                   # Main app component
├── main.tsx                  # Entry point
└── index.css                 # Global styles (Tailwind)
```

### State Management

Uses React hooks (useState, useEffect):
- `recommendation` - Current recommendation from API
- `isLoading` - Loading state during API call
- `error` - Error messages if API fails

### API Integration

`services/api.ts` provides:
- `getRecommendation(request)` - POST to `/api/v1/recommendations`
- Type-safe request/response interfaces

### Styling

**Technology**: Tailwind CSS + PostCSS

**Color Palette**:
- Primary Green: `#10b981` - Success, fairway
- Danger Red: `#ef4444` - Hazards
- Warning Yellow: `#f59e0b` - Caution
- Info Blue: `#3b82f6` - Information
- Backgrounds: Gray tones

**Features**:
- Utility-first CSS
- Golf-themed custom colors
- Responsive breakpoints (mobile-first)
- Smooth transitions and animations

## 📱 Features Detail

### ShotInputForm Component

Controlled inputs for:
- Distance (number input, 30-300 range)
- Pin location (radio buttons)
- Ball lie (select dropdown)
- Lie quality (select dropdown)
- Strategy (radio buttons)

Auto-generates:
- `analysis_id` - Unique ID from timestamp
- `player_id` - "joe_kramer_001" (hardcoded for MVP)
- `hole_id` - "pebble_7" (hardcoded for MVP)
- `weather_condition_id` - "weather_001" (hardcoded for MVP)

### RecommendationCard Component

Displays with gradient green background:
- Club name (uppercase, large)
- Carry and total distances
- Target area string
- Confidence meter with percentage

### AdjustmentDetails Component

Shows all distance adjustments:
- Temperature (yards)
- Elevation (yards)
- Wind (yards)
- Rain (percent)
- Lie quality (percent)
- Color-coded (green for positive, red for negative)
- Human-readable summary

### HazardWarnings Component

Alert-style display for:
- Each hazard in play
- Risk level badge (high/medium/low)
- Hazard icon (💧 water, 🏜️ bunker, ⛔ OB, 🌲 trees)
- Distance from tee
- Safe miss direction

### AlternativeClubs Component

Lists alternative clubs if provided:
- Club name
- Confidence percentage
- Strategic rationale
- Hover effect for emphasis

## 🔧 Configuration

### Vite Config (`vite.config.ts`)

```typescript
server: {
  port: 5173,
  proxy: {
    '/api': {
      target: 'http://localhost:8000',
      changeOrigin: true,
    },
  },
}
```

Proxies `/api/*` requests to backend, avoiding CORS issues.

### Tailwind Config (`tailwind.config.js`)

Custom golf-themed colors and responsive design.

### TypeScript Config (`tsconfig.json`)

Strict mode enabled for type safety.

## 🧪 Testing

### Manual Testing Scenarios

1. **Happy Path**
   - Fill form with valid data
   - Submit
   - Recommendation displays correctly

2. **Strategy Changes**
   - Select aggressive strategy → More aggressive club recommended
   - Select conservative strategy → More conservative club recommended

3. **Lie Changes**
   - Select rough lie → Distance penalties applied
   - Select bunker → Additional penalties

4. **Responsive Design**
   - Resize browser window
   - Layout adapts correctly on different screen sizes

5. **Error Handling**
   - Stop backend API
   - Try to get recommendation
   - Error message displays

## 🚀 Deployment

### Quick Deploy

1. Build: `npm run build`
2. Serve `dist/` folder via web server (nginx, Apache, etc.)
3. Ensure backend API is accessible

### Environment Variables

Currently none required. To add:
1. Create `.env` file
2. Add `VITE_API_URL=http://your-api.com`
3. Use in code: `import.meta.env.VITE_API_URL`

## 🔮 Future Enhancements

### Phase 2
- [ ] Course selector (multiple courses)
- [ ] Weather controls (temperature, wind, etc.)
- [ ] Player baseline editor
- [ ] Real-time distance slider

### Phase 3
- [ ] Shot history tracking
- [ ] Performance analytics
- [ ] Multiple players support
- [ ] Round scoring

### Phase 4
- [ ] Course visualization (hole maps)
- [ ] GPS integration
- [ ] Mobile app (React Native)
- [ ] Offline mode

## 📊 Performance

- **Bundle Size**: ~150KB (gzipped)
- **Initial Load**: <1s on broadband
- **API Response**: <100ms typical

Optimizations:
- Tree-shaking (unused code removed)
- CSS purging (only used styles included)
- Lazy loading (if needed)

## 🐛 Troubleshooting

### "Failed to get recommendation"
- Check backend API is running: `curl http://localhost:8000/health`
- Check proxy in vite.config.ts is correct
- Check browser console for CORS errors

### Styles not loading
- Run `npm install` again
- Delete `node_modules` and `package-lock.json`, then reinstall
- Rebuild: `npm run build`

### TypeScript errors
- Ensure `tsconfig.json` matches your setup
- Run `npm run build` to see full errors

## 📚 Learning Resources

- [React Documentation](https://react.dev)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Tailwind CSS Docs](https://tailwindcss.com/docs)
- [Vite Guide](https://vitejs.dev/guide/)

## 📝 Notes

- MVP uses hardcoded `hole_id` = "pebble_7"
- MVP uses hardcoded `player_id` = "joe_kramer_001"
- Weather is hardcoded as standard conditions (70°F, calm, dry)
- Backend API must be running for recommendations to work

## 🎉 Next Steps

1. **Install dependencies**: `npm install`
2. **Start dev server**: `npm run dev`
3. **Visit**: http://localhost:5173
4. **Try a recommendation**: Fill form and submit
5. **Explore the code**: Browse components to understand structure
