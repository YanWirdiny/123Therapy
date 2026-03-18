# 123Therapy — Development TODO

> Format: Each task has a status, estimated execution time, and clear scope.
> Status: `[ ]` pending · `[~]` in progress · `[x]` done

---

## PHASE 0 — v2.0 Mode System (Solo / Duo / Group)
**Date added:** 2026-03-17
**Goal:** Extend the app from couples-only to Solo, Duo, and Group modes with adapted prompts.

---

### Task 0.1 — Update `participant.py`: Add new roles
**File:** `app/models/participant.py`
**Est. time:** 5 min
**Status:** `[X]` at 8:37  03-17-2026

**What to change:**
- Add `SOLO = "solo"` to `ParticipantRole` enum — used when mode is solo
- Add `MEMBER_A`, `MEMBER_B`, `MEMBER_C`, `MEMBER_D` to `ParticipantRole` — used when mode is group

**Why:** The current model only has `PARTNER_A` and `PARTNER_B`. Solo and group participants need their own role identifiers so the AI prompt and UI can reference them correctly.

---

### Task 0.2 — Update `room.py`: Add mode + relationship type, dynamic capacity
**File:** `app/models/room.py`
**Est. time:** 20 min
**Status:** `[~]` in progress — steps 1–6 done, steps 7–8 remaining

**What to change:**

1. `[x]` Add `RoomMode` enum with values: `SOLO`, `DUO`, `GROUP`

2. `[x]` Add `RelationshipType` enum with values: `COUPLE`, `FRIENDS`, `FAMILY`, `OTHER`
   - `FAMILY` covers siblings, parent/child, and extended family dynamics (broader than siblings alone)
   - Only relevant when `mode == DUO`
   - GROUP does not use `relationship_type` (deferred to future release)

3. `[x]` Fix timezone inconsistency: `created_at` and `is_expired()` now use `datetime.now(timezone.utc)`
   — consistent with `Participant` timestamps, no more naive/aware mixing.

4. `[x]` Added `mode` and `relationship_type` fields to `Room` dataclass.
   Replaced `MAX_PARTICIPANTS = 2` class variable with `__post_init__` setting `self.max_participants`:
   - SOLO → 1 · DUO → 2 · GROUP → 4

5. `[x]` Updated `add_participant()` role assignment logic:
   - SOLO → `ParticipantRole.SOLO`
   - DUO → `PARTNER_A` / `PARTNER_B` by join order
   - GROUP → `MEMBER_A` through `MEMBER_D` by join order

6. `[x]` Renamed `both_connected()` → `is_session_ready()` with mode-aware logic.
   `both_connected()` kept as deprecated alias — nothing breaks.

7. `[ ]` Update `to_dict()` to include `mode` and `relationship_type`

8. `[ ]` Add `create_solo()`, `create_duo(relationship_type)`, `create_group()` factory classmethods alongside existing `create()`

**Why:** The `Room` model is the core data object. Every other change depends on the mode being stored here. Getting this right before touching prompts or events prevents cascading rework.

---

### Task 0.3 — Update `prompt_templates.py`: Solo prompt, Duo variants, Group prompt
**File:** `app/services/prompt_templates.py`
**Est. time:** 30 min
**Status:** `[ ]`

**What to change:**

1. Rename existing `THERAPIST_SYSTEM_PROMPT` → `DUO_COUPLE_SYSTEM_PROMPT` (it was written for couples)

2. Add `SOLO_SYSTEM_PROMPT`:
   - AI is an individual therapist, not couples mediator
   - Focus: personal reflection, self-awareness, emotional processing
   - No references to "Partner A/B" — address the person directly as "you"
   - Shorter, more conversational tone

3. Add `DUO_FRIENDS_SYSTEM_PROMPT`:
   - Adapted for platonic friendship conflicts
   - Focus: communication breakdown, boundary setting, loyalty vs. honesty tensions
   - Address as "Person A / Person B"

4. Add `DUO_FAMILY_SYSTEM_PROMPT`:
   - Adapted for family dynamics (siblings, parent/child, extended family)
   - Focus: family history patterns, generational roles, loyalty conflicts, caregiving tensions
   - Address as "Person A / Person B"

5. Add `DUO_OTHER_SYSTEM_PROMPT`:
   - Neutral version for unspecified relationships
   - Generic interpersonal conflict guidance

6. Add `GROUP_SYSTEM_PROMPT`:
   - Generic group therapy facilitation (no relationship subtype — future feature)
   - Focus: giving each voice equal space, preventing one person from dominating, identifying shared themes
   - Address participants as "Member A / Member B / Member C / Member D"
   - Note in code: `# TODO: Group relationship subtypes (family, friend group, etc.) — future feature`

7. Add welcome messages per mode/relationship:
   - `SOLO_WELCOME_MESSAGE`
   - `DUO_COUPLE_WELCOME_MESSAGE` (existing `WELCOME_MESSAGE` renamed)
   - `DUO_FRIENDS_WELCOME_MESSAGE`
   - `DUO_FAMILY_WELCOME_MESSAGE`
   - `GROUP_WELCOME_MESSAGE`

8. Add helper function: `get_system_prompt(mode, relationship_type) -> str`
   - For `SOLO`: ignore `relationship_type`, return `SOLO_SYSTEM_PROMPT`
   - For `DUO`: branch on `relationship_type` → couple/friends/family/other
   - For `GROUP`: ignore `relationship_type`, return `GROUP_SYSTEM_PROMPT`
   - Single place to control all prompt routing

9. Add helper function: `get_welcome_message(mode, relationship_type) -> str`
   - Same pattern as above, returns the correct welcome message

**Why:** The prompt IS the therapist. A couples prompt used for siblings or a solo session will produce wrong, confusing AI responses. Each context needs its own therapeutic framing. GROUP has one generic prompt for now — relationship subtypes are deferred to a future release.

---

### Task 0.4 — Update `gemini_service.py`: Multi-mode prompt routing
**File:** `app/services/gemini_service.py`
**Est. time:** 20 min
**Status:** `[ ]`

**What to change:**

1. Replace single `_model` with a `_models: dict` cache, keyed by `(RoomMode, RelationshipType)`

2. Add private method `_get_model(room: Room)`:
   - Checks `_models` cache for the key `(room.mode, room.relationship_type)`
   - If not found: calls `get_system_prompt(room.mode, room.relationship_type)`, creates a new `GenerativeModel` with that system_instruction, stores in cache
   - Returns the correct model

3. Update `generate_response(room)` to call `self._get_model(room)` instead of `self._model`

4. Update `get_welcome_message()` → `get_welcome_message(room: Room)`:
   - Calls `get_welcome_message(room.mode, room.relationship_type)` from prompt_templates
   - Returns the correct welcome message for that room type

5. Remove `initialize_gemini_client()` call from `generate_response` — lazy init moves into `_get_model()`

**Why:** The current singleton hard-codes one system prompt at initialization. Multi-mode requires different system instructions per room context. A model cache avoids recreating the same model for every message.

---

### Task 0.5 — Update `events.py`: Mode-aware session flow
**File:** `app/websocket/events.py`
**Est. time:** 25 min
**Status:** `[ ]`

**What to change:**

1. Update `handle_create_room(data)`:
   - Accept `mode` (default `"duo"`) and `relationship_type` (default `None`) from event data
   - Call `room_store.create_room(mode, relationship_type)` instead of `room_store.create_room()`
   - For `SOLO` mode: after creating the room, **auto-join** the creator as a participant in the same event handler — no separate `join_room` call needed from the client
   - Emit `room_created` with `mode` included in response

2. Update `handle_join_room(data)`:
   - Keep existing logic for DUO and GROUP
   - For SOLO: this path won't be hit (auto-joined on create), but add a guard just in case

3. Update session-ready trigger (currently fires when `PARTNER_B` joins):
   - Replace `if participant.role == ParticipantRole.PARTNER_B` check with `if room.is_session_ready()`
   - This handles all modes correctly without special-casing

4. Update the `partner_disconnected` / `partner_left` events:
   - For SOLO: emit `session_paused` instead (there's no partner to notify)
   - For GROUP: message should say "A participant has disconnected" not "Your partner"

5. Update AI welcome message trigger to use `gemini_service.get_welcome_message(room)` instead of hardcoded string

**Why:** The session-start logic is tightly coupled to the DUO model. Replacing the `PARTNER_B` role check with `is_session_ready()` makes it mode-agnostic — we only change one line instead of branching everywhere.

---

### Task 0.6 — Update `rooms.py` API: Accept mode + relationship_type
**File:** `app/api/rooms.py`
**Est. time:** 15 min
**Status:** `[ ]`

**What to change:**

1. Update `create_room()` POST endpoint:
   - Parse JSON body for `mode` (default `"duo"`) and `relationship_type` (default `None`)
   - Validate `mode` is one of: `solo`, `duo`, `group`
   - Validate `relationship_type` is one of: `couple`, `friends`, `family`, `other`, or absent
   - Pass validated values to `room_store.create_room(mode, relationship_type)`
   - Return `mode` in the response body

2. Update `get_room()` response to include `mode` and `relationship_type`

3. Update `get_stats()` to count rooms by mode (useful for monitoring later):
   - `solo_rooms`, `duo_rooms`, `group_rooms`

**Why:** The API is how the frontend will tell the backend what type of session to create. Without this, the frontend has no way to set the mode.

---

### Task 0.7 — Update `room_store.py`: Support mode + relationship_type on creation
**File:** `app/services/room_store.py`
**Est. time:** 10 min
**Status:** `[ ]`

**What to change:**
- Read the file first (not yet read)
- Update `create_room()` method to accept and pass through `mode` and `relationship_type` to `Room` factory

---

## PHASE 1 — Infrastructure Foundation
*(To be planned after Phase 0 is complete and the data model is stable)*

---

## Notes
- All Phase 0 tasks are **backend only** — no frontend changes yet
- Tasks 0.1 → 0.2 → 0.3 must be done in order (each builds on the last)
- Tasks 0.4, 0.5, 0.6, 0.7 can be done in any order after 0.1–0.3 are complete
- No database changes needed — still in-memory (that's Phase 1)
