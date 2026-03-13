# Couples Therapy Web App - Project Notes

## Project Overview

A web application that provides couples with AI-assisted preliminary therapy sessions using Google's Gemini AI. The platform enables two partners to connect in a virtual room and engage in guided therapeutic conversations with an AI therapist that can identify serious issues and recommend professional help when needed.

---

## Core Concept

**What It Does:**
- Creates private virtual therapy rooms for couples
- Facilitates real-time text conversations between partners and Gemini AI
- AI acts as a couples therapist, asking questions and providing guidance
- Detects serious issues requiring professional intervention
- Provides resources and specialist referrals when needed

**What It's NOT:**
- Not a replacement for professional therapy
- Not a crisis intervention service
- Not a long-term therapy solution
- Not a platform for storing sensitive data permanently

---

## Technology Stack

### Backend
- **Framework:** Flask (Python)
- **Real-time Communication:** Flask-SocketIO (WebSockets)
- **AI Integration:** Google Gemini AI API
- **Session Storage:** In-memory (Python dict) → Later: Redis/SQLite
- **Environment:** Python 3.8+

### Frontend
- **Structure:** HTML5
- **Styling:** Tailwind CSS
- **Interactivity:** Vanilla JavaScript
- **Target Devices:** Mobile phones & Laptops (responsive design)

### Communication Protocol
- **WebSocket:** Real-time bidirectional communication
- **REST API:** Room creation, session management

---

## Application Roles & Components

### 1. Room Manager
**Responsibilities:**
- Generate unique 6-digit room codes
- Create and destroy virtual rooms
- Manage room lifecycle (2-hour timeout)
- Enforce 2-person limit per room
- Handle room state (active, expired, closed)

**Key Functions:**
```
- create_room() → returns room_code
- join_room(room_code, user_id) → success/failure
- validate_room(room_code) → active/expired/invalid
- close_room(room_code) → cleanup
```

---

### 2. WebSocket Handler
**Responsibilities:**
- Manage real-time connections
- Route messages between partners and AI
- Handle connect/disconnect events
- Maintain connection state
- Enable reconnection within 5-minute window

**Key Events:**
```
- on_connect: Establish socket connection
- on_join_room: Add user to specific room
- on_message: Broadcast to room + Gemini
- on_disconnect: Handle graceful exit
- on_reconnect: Restore session state
```

---

### 3. Gemini AI Therapist
**Responsibilities:**
- Maintain conversation context per room
- Ask therapeutic questions
- Provide evidence-based relationship guidance
- Distinguish between Partner A and Partner B responses
- Generate empathetic, professional responses

**System Prompt Guidelines:**
```
- Act as empathetic couples therapist
- Ask open-ended questions
- Validate both partners' feelings
- Identify communication patterns
- Provide actionable advice
- Remain neutral and non-judgmental
```

---

### 4. Crisis Detection System
**Responsibilities:**
- Monitor conversation for red-flag keywords
- Detect patterns indicating serious issues
- Trigger specialist referral protocol
- Provide crisis resources

**Flag Categories:**

**Category 1: Violence/Abuse**
- Keywords: "hit", "hurt", "afraid", "violent", "abuse", "attack", "threaten"
- Action: Immediate specialist referral + crisis hotline

**Category 2: Mental Health Crisis**
- Keywords: "suicide", "kill myself", "end it all", "hopeless", "worthless"
- Action: Mental health crisis resources + emergency contacts

**Category 3: Severe Infidelity/Betrayal**
- Patterns: Multiple affairs, ongoing deception
- Action: Recommend professional therapist specializing in betrayal trauma

**Category 4: Substance Abuse**
- Keywords: "addiction", "can't stop drinking", "drugs", "alcohol problem"
- Action: Addiction specialist referral + support groups

**Category 5: Severe Communication Breakdown**
- Patterns: Constant contempt, stonewalling, complete disconnect
- Action: Recommend Gottman Method therapist or couples counselor

**Response Protocol:**
```
1. Stop normal therapy conversation
2. Display: "Based on what you've shared, this situation requires professional support."
3. Show specific resources (hotlines, specialist types, local options)
4. Offer conversation export for real therapist
5. Provide option to continue with disclaimer OR end session
```

---

### 5. Session Manager
**Responsibilities:**
- Track session duration
- Store conversation history (temporary)
- Provide export functionality
- Handle session expiration
- Clear data after session ends

**Session Lifecycle:**
```
1. Created: Room code generated
2. Active: Both partners connected
3. In-Progress: Conversation ongoing
4. Flagged: Crisis detected (optional state)
5. Ended: Partners leave OR timeout
6. Expired: Data deleted (immediate or 10 min grace)
```

---

## Development Roadmap

### **PHASE 1: Backend Core (Week 1-2)**

#### Milestone 1.1: Room Management System
- [ ] Implement room code generation (6-digit alphanumeric)
- [ ] Create in-memory room storage (dict structure)
- [ ] Build room creation endpoint
- [ ] Build room validation logic
- [ ] Implement 2-person limit enforcement
- [ ] Add room expiration (2-hour timeout)
- [ ] **Test:** Create room, validate code, enforce limits

#### Milestone 1.2: WebSocket Communication
- [ ] Set up Flask-SocketIO
- [ ] Implement connection handling
- [ ] Build join_room event
- [ ] Build send_message event
- [ ] Implement disconnect handling
- [ ] Add reconnection logic (5-min window)
- [ ] **Test:** Two browser tabs, join room, exchange messages

#### Milestone 1.3: Gemini AI Integration
- [ ] Set up Gemini API credentials
- [ ] Create therapist system prompt
- [ ] Implement conversation context management
- [ ] Build message formatting (Partner A/B labels)
- [ ] Integrate AI responses into WebSocket flow
- [ ] **Test:** Send messages, verify AI responses, check context retention

#### Milestone 1.4: Crisis Detection
- [ ] Create flag keyword dictionary
- [ ] Implement keyword scanning algorithm
- [ ] Build crisis response templates
- [ ] Add specialist resource database
- [ ] Integrate crisis protocol into message flow
- [ ] **Test:** Trigger each flag category, verify responses

#### Milestone 1.5: Session Management
- [ ] Implement conversation history storage
- [ ] Add session export functionality (JSON/TXT)
- [ ] Build session timeout mechanism
- [ ] Create data cleanup on session end
- [ ] **Test:** Full session flow, export data, verify cleanup

---

### **PHASE 2: Backend Testing (Week 2)**

#### Milestone 2.1: Create Basic Test Interface
- [ ] Build minimal HTML forms (no styling)
- [ ] Create room creation form
- [ ] Create room join form
- [ ] Add simple chat interface
- [ ] Display AI responses
- [ ] **Purpose:** Test all backend functionality

#### Milestone 2.2: Integration Testing
- [ ] Test complete user journey (create → join → chat → crisis → export → end)
- [ ] Test edge cases (disconnect, timeout, invalid codes)
- [ ] Test concurrent rooms (multiple couples simultaneously)
- [ ] Verify Gemini context isolation between rooms
- [ ] Load test WebSocket connections

#### Milestone 2.3: Security & Privacy Review
- [ ] Ensure room codes are cryptographically random
- [ ] Verify no data leakage between rooms
- [ ] Test session isolation
- [ ] Implement rate limiting
- [ ] Add input sanitization

---

### **PHASE 3: Frontend Design (Week 3-4)**

#### Milestone 3.1: Design System Setup
- [ ] Set up Tailwind CSS
- [ ] Define color palette (calming, professional)
- [ ] Create component library (buttons, inputs, cards)
- [ ] Design responsive layouts (mobile-first)

#### Milestone 3.2: Core UI Pages
- [ ] Landing page with disclaimers
- [ ] Room creation interface
- [ ] Room join interface
- [ ] Chat interface (mobile & desktop)
- [ ] Crisis alert modal
- [ ] Resource display page
- [ ] Session export page

#### Milestone 3.3: UX Enhancements
- [ ] Typing indicators
- [ ] Message timestamps
- [ ] Partner online/offline status
- [ ] Smooth scrolling chat
- [ ] Mobile keyboard optimization
- [ ] Accessibility features (ARIA labels, screen readers)

---

### **PHASE 4: Polish & Deploy (Week 4-5)**

#### Milestone 4.1: Content & Legal
- [ ] Write comprehensive disclaimer
- [ ] Create crisis resource database (hotlines, specialists)
- [ ] Add terms of service
- [ ] Privacy policy
- [ ] FAQ section

#### Milestone 4.2: Production Preparation
- [ ] Environment variable management
- [ ] Error handling & logging
- [ ] Performance optimization
- [ ] Database migration (if moving from in-memory)
- [ ] Deployment setup (Heroku, Railway, or VPS)

#### Milestone 4.3: Launch
- [ ] Beta testing with real users
- [ ] Bug fixes
- [ ] Final security audit
- [ ] Deploy to production
- [ ] Monitor initial usage

---

## Key Features Summary

### Must-Have (MVP)
✅ Virtual room creation with unique codes  
✅ Real-time WebSocket chat between two partners  
✅ Gemini AI acting as therapist  
✅ Crisis keyword detection  
✅ Specialist referral system  
✅ Session export functionality  
✅ Mobile-responsive design  
✅ Strong disclaimers  

### Nice-to-Have (Future)
⭐ User accounts (optional, for session history)  
⭐ Video/audio support  
⭐ Scheduled sessions  
⭐ Therapist directory integration  
⭐ Progress tracking over multiple sessions  
⭐ Multilingual support  

### Out of Scope (Won't Build)
❌ Payment processing  
❌ Direct therapist booking  
❌ Medical record storage  
❌ Emergency services dispatch  

---

## Critical Design Principles

1. **Privacy First:** No permanent data storage without explicit consent
2. **Safety First:** Crisis detection must be robust and conservative
3. **Transparency:** Clear about AI limitations and when human help is needed
4. **Accessibility:** Works on low-bandwidth connections, simple interface
5. **Empathy:** Tone should be warm, non-judgmental, supportive

---

## Technical Decisions Log

### Decision 1: In-Memory vs Database
**Choice:** Start with in-memory (Python dict)  
**Reason:** Faster development, no data persistence concerns  
**Future:** Migrate to Redis for production scalability  

### Decision 2: WebSocket vs Polling
**Choice:** WebSocket (Flask-SocketIO)  
**Reason:** True real-time communication, better UX  
**Trade-off:** Slightly more complex deployment  

### Decision 3: Gemini vs OpenAI
**Choice:** Google Gemini AI  
**Reason:** Cost-effective, good instruction following, handles context well  
**Alternative:** Could switch to Claude or GPT if needed  

### Decision 4: Authentication
**Choice:** No user accounts (anonymous room codes)  
**Reason:** Reduces friction, privacy-focused  
**Trade-off:** No session history across devices  

---

## Questions to Answer Before Coding

### Room Management
**Q1:** How do partners coordinate joining?  
**Options:**  
- A) Partner 1 creates room → shares code → Partner 2 joins  
- B) Both partners agree on code beforehand, both "create/join"  

**Decision Needed:** [ ]

---

### Session Data
**Q2:** What happens to conversation after session?  
**Options:**  
- A) Delete immediately when both leave  
- B) Allow 10-minute export window, then delete  
- C) Keep for 24 hours with encrypted access  

**Decision Needed:** [ ]

---

### Gemini Interaction
**Q3:** How does the conversation flow?  
**Options:**  
- A) Gemini asks question → Partner A answers → Partner B answers → Gemini responds  
- B) Partners chat freely → Gemini observes and interjects  
- C) Hybrid: Gemini guides with questions but partners can talk to each other  

**Decision Needed:** [ ]

---

### Crisis Handling
**Q4:** What happens when crisis is detected?  
**Options:**  
- A) Show warning + resources, allow continuation with disclaimer  
- B) Force session end, show resources only  
- C) Pause session, require acknowledgment, then continue or end  

**Decision Needed:** [ ]

---

## Next Steps

1. Answer the 4 critical questions above
2. Set up development environment
3. Start Phase 1, Milestone 1.1 (Room Management)
4. Build and test backend with zero design
5. Move to frontend only after backend is solid

---

## Notes & Ideas

- Consider adding a "practice mode" with AI playing both partners for demo
- Could add pre-session questionnaire to give Gemini context
- Explore voice-to-text for accessibility
- Consider adding recommended session structure (intro → issue exploration → action planning)

---

**Last Updated:** January 31, 2026  
**Project Status:** Planning Phase  
**Developer Level:** Intermediate  
**Estimated Timeline:** 4-5 weeks to MVP

123Therapy 2.0

**Goal** 
Migrate for a couple AI therapy only to a more general system open to everyone. 
Utilization 123Therapy for deeper intermediate for a  therapist and his new clients.

Update  the whole application but implementing: 
- Universality by  implementing 3 mode of utilization 
    - Solo for personal communication with the AI therapist.
    - Duo that is current state usable for Couples, Friends, Siblings
    - Group MAX  of 4 Persons 

# Insight on each mode 
**SOLO**
- Solo conversation will feature Eleven labs for TTS and STT for  quicker and more personal experience. 
- Updates of the AI Prompt for a MORE adapted service and personalized.

**DUO**
Current developed mode we need to keep it as it is but change prompt to adapt to the relativity of the persons 
- couple, siblings, friends should be having different treatment and adapted question.
(Need brainstorming to  update the method of communication in between both individuals).\
- Nature of relation will be ask as a drop down at the start of the chat and parse to Gemini 
    for prompting adaptation

**GROUP**
BETA
- Implement rule for limiting room for 4 people 
- adapt AI to group conversation and better context handling from different sources.

**GENERAL** 
-Not being implemented yet-
- A service of personalisation by choosing avatar for the AI  including  a different style of therapist  in term of communication. 

- Upgrade of the AI chat UI  to for easier  reading and understanding for the general users.

-ability to email your chat to your chosen therapist for context for your first  meeting.


**FURTHER GOAL**
Implement a process for  Therapist to assign pre-assessment to their patient  for knowledge context for meeting

---
**Last Updated:** March 12, 2026  
**Project Status:** Implementation  2.0