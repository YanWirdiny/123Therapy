# Frontend Design Specification

## Design Philosophy
Calming, zen-like atmosphere reminiscent of a professional therapy room. The interface should feel safe, warm, and supportive.

---

## Color Palette

### Core Colors
| Name | Hex | RGB | Usage |
|------|-----|-----|-------|
| Sage Green | `#8FAE8B` | 143, 174, 139 | Primary buttons, CTAs |
| Soft Blue | `#A8C5D6` | 168, 197, 214 | Links, secondary accents |
| Warm White | `#FAF9F6` | 250, 249, 246 | Page background |
| Light Sand | `#F5F1EB` | 245, 241, 235 | Cards, chat container |
| Charcoal | `#3D3D3D` | 61, 61, 61 | Primary text |
| Warm Gray | `#6B6B6B` | 107, 107, 107 | Secondary text |

### Chat Bubble Colors
| Role | Hex | Usage |
|------|-----|-------|
| Partner A | `#7EB5A6` | Left-aligned bubbles |
| Partner B | `#D4A5A5` | Right-aligned bubbles |
| AI Therapist | `#B8A9C9` | Center-aligned bubbles |
| System | `#E8E4DF` | Notifications, timestamps |

### Status Colors
| State | Hex | Usage |
|-------|-----|-------|
| Success | `#8FAE8B` | Confirmations |
| Warning | `#E8C87D` | Cautions |
| Crisis | `#E8A598` | Crisis alerts |
| Error | `#D4A5A5` | Errors |

---

## Typography

### Font Stack
```css
font-family: 'Inter', 'Segoe UI', system-ui, -apple-system, sans-serif;
```

### Scale
| Element | Size | Weight | Line Height |
|---------|------|--------|-------------|
| H1 | 2.5rem (40px) | 600 | 1.2 |
| H2 | 2rem (32px) | 600 | 1.3 |
| H3 | 1.5rem (24px) | 500 | 1.4 |
| Body | 1rem (16px) | 400 | 1.6 |
| Small | 0.875rem (14px) | 400 | 1.5 |
| Chat | 0.9375rem (15px) | 400 | 1.5 |

---

## Page Structure

### Routes
```
/                    -> Landing page
/room/create         -> Create new room
/room/join           -> Join existing room
/room/<code>/chat    -> Chat interface
/room/<code>/export  -> Export session
```

---

## Page Layouts

### 1. Landing Page (`/`)

```
+----------------------------------------------------------+
|  [Logo]                              [About] [Resources]  |
+----------------------------------------------------------+
|                                                          |
|              Welcome to 123Therapy                       |
|                                                          |
|     A safe space for couples to communicate              |
|     with AI-guided support                               |
|                                                          |
|         [Start a Session]  [Join Partner]                |
|                                                          |
+----------------------------------------------------------+
|                    DISCLAIMER                            |
|  This is not a replacement for professional therapy.     |
|  If you are in crisis, please contact emergency services.|
+----------------------------------------------------------+
|                     Footer                               |
+----------------------------------------------------------+
```

**Elements:**
- Hero section with calming gradient background
- Clear value proposition
- Two primary CTAs
- Prominent disclaimer
- Resources/crisis hotline links in footer

---

### 2. Create Room (`/room/create`)

```
+----------------------------------------------------------+
|  [<- Back]                                     123Therapy |
+----------------------------------------------------------+
|                                                          |
|              Create a Therapy Room                       |
|                                                          |
|     +------------------------------------------+         |
|     |                                          |         |
|     |     Your room code is:                   |         |
|     |                                          |         |
|     |          [ A B C 1 2 3 ]                 |         |
|     |                                          |         |
|     |     Share this code with your partner    |         |
|     |                                          |         |
|     |     [Copy Code]  [Enter Room]            |         |
|     |                                          |         |
|     +------------------------------------------+         |
|                                                          |
|     Waiting for partner to join...                       |
|     [=====>                    ] 0/2 connected           |
|                                                          |
+----------------------------------------------------------+
```

---

### 3. Join Room (`/room/join`)

```
+----------------------------------------------------------+
|  [<- Back]                                     123Therapy |
+----------------------------------------------------------+
|                                                          |
|                Join Your Partner                         |
|                                                          |
|     +------------------------------------------+         |
|     |                                          |         |
|     |     Enter the 6-digit room code:         |         |
|     |                                          |         |
|     |     [ _ ] [ _ ] [ _ ] [ _ ] [ _ ] [ _ ]  |         |
|     |                                          |         |
|     |              [Join Room]                 |         |
|     |                                          |         |
|     +------------------------------------------+         |
|                                                          |
+----------------------------------------------------------+
```

---

### 4. Chat Interface (`/room/<code>/chat`)

```
+----------------------------------------------------------+
|  [End Session]     Room: ABC123     [Partner: Connected] |
+----------------------------------------------------------+
|                                                          |
|  +----------------------------------------------------+  |
|  |                                                    |  |
|  |  [Partner A bubble]                                |  |
|  |  "I feel like we never talk anymore"               |  |
|  |                              10:32 AM              |  |
|  |                                                    |  |
|  |                         [Your bubble]              |  |
|  |              "That's not fair, I try to talk"      |  |
|  |                              10:33 AM              |  |
|  |                                                    |  |
|  |            [AI Therapist bubble]                   |  |
|  |    "I hear both of you. Partner A, it sounds      |  |
|  |     like you're feeling disconnected..."          |  |
|  |                              10:33 AM              |  |
|  |                                                    |  |
|  |                    ... typing                      |  |
|  +----------------------------------------------------+  |
|                                                          |
|  +----------------------------------------------------+  |
|  | [Type your message...                    ] [Send]  |  |
|  +----------------------------------------------------+  |
|                                                          |
+----------------------------------------------------------+
```

**Chat Features:**
- Messages grouped by sender
- Timestamps on each message
- Typing indicators
- Auto-scroll to newest
- Partner connection status

---

### 5. Crisis Modal (Overlay)

```
+----------------------------------------------------------+
|                                                          |
|     +------------------------------------------+         |
|     |  [!] We're Here to Help                  |         |
|     |------------------------------------------|         |
|     |                                          |         |
|     |  Based on what's been shared, we want    |         |
|     |  to make sure you have the support you   |         |
|     |  need.                                   |         |
|     |                                          |         |
|     |  RESOURCES:                              |         |
|     |  - National Hotline: 1-800-XXX-XXXX      |         |
|     |  - Crisis Text Line: Text HOME to 741741|         |
|     |  - Emergency: 911                        |         |
|     |                                          |         |
|     |  [Continue Session]  [Find a Therapist] |         |
|     |                                          |         |
|     +------------------------------------------+         |
|                                                          |
+----------------------------------------------------------+
```

---

## Components

### Buttons

```css
/* Primary Button */
.btn-primary {
  background: #8FAE8B;
  color: white;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-primary:hover {
  background: #7A9A76;
  transform: translateY(-1px);
}

/* Secondary Button */
.btn-secondary {
  background: transparent;
  color: #8FAE8B;
  border: 2px solid #8FAE8B;
  padding: 10px 22px;
  border-radius: 8px;
}
```

### Chat Bubbles

```css
/* Base bubble */
.bubble {
  max-width: 70%;
  padding: 12px 16px;
  border-radius: 18px;
  margin: 4px 0;
}

/* Partner A - Left */
.bubble-partner-a {
  background: #7EB5A6;
  color: white;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
}

/* Partner B (You) - Right */
.bubble-partner-b {
  background: #D4A5A5;
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

/* AI Therapist - Center */
.bubble-ai {
  background: #B8A9C9;
  color: white;
  align-self: center;
  max-width: 80%;
  border-radius: 12px;
}
```

### Input Field

```css
.input-message {
  width: 100%;
  padding: 14px 16px;
  border: 2px solid #E8E4DF;
  border-radius: 24px;
  font-size: 15px;
  transition: border-color 0.2s;
}

.input-message:focus {
  border-color: #8FAE8B;
  outline: none;
}
```

### Cards

```css
.card {
  background: #F5F1EB;
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
}
```

---

## Responsive Breakpoints

```css
/* Mobile */
@media (max-width: 639px) { }

/* Tablet */
@media (min-width: 640px) and (max-width: 1023px) { }

/* Desktop (primary) */
@media (min-width: 1024px) { }

/* Large Desktop */
@media (min-width: 1280px) { }
```

### Desktop First Approach
- Design for 1024px+ first
- Scale down for tablet (640-1023px)
- Adapt for mobile (<640px)

---

## Tailwind CSS Configuration

```javascript
// tailwind.config.js
module.exports = {
  content: ["./templates/**/*.html", "./static/**/*.js"],
  theme: {
    extend: {
      colors: {
        'sage': {
          DEFAULT: '#8FAE8B',
          light: '#A8C5A5',
          dark: '#7A9A76',
        },
        'sky': {
          soft: '#A8C5D6',
        },
        'sand': {
          light: '#F5F1EB',
          DEFAULT: '#E8E4DF',
        },
        'warm-white': '#FAF9F6',
        'charcoal': '#3D3D3D',
        'warm-gray': '#6B6B6B',
        'partner-a': '#7EB5A6',
        'partner-b': '#D4A5A5',
        'ai-therapist': '#B8A9C9',
        'crisis': '#E8A598',
      },
      fontFamily: {
        sans: ['Inter', 'Segoe UI', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        'bubble': '18px',
      },
    },
  },
  plugins: [],
}
```

---

## File Structure

```
templates/
  base.html           <- Shared layout
  index.html          <- Landing page
  room/
    create.html       <- Create room
    join.html         <- Join room
    chat.html         <- Chat interface
    export.html       <- Export session

static/
  css/
    styles.css        <- Compiled Tailwind
  js/
    app.js            <- Main app logic
    socket.js         <- WebSocket handling
    chat.js           <- Chat functionality
  images/
    logo.svg
    icons/
```

---

## Accessibility Requirements

- All interactive elements keyboard accessible
- ARIA labels on buttons and inputs
- Color contrast ratio minimum 4.5:1
- Focus indicators visible
- Screen reader friendly chat messages
- Reduced motion support

---

## Animation Guidelines

- Subtle transitions (200-300ms)
- Ease-out for entrances
- No distracting animations
- Typing indicator: gentle pulse
- Message appear: fade + slide up

```css
@keyframes fadeSlideUp {
  from {
    opacity: 0;
    transform: translateY(8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.message-enter {
  animation: fadeSlideUp 0.2s ease-out;
}
```

---

**Status:** Design Specification Complete
**Next:** Implementation Phase 3
