# Student-Focused Features

Five powerful features designed specifically for college students using NoteGPT to enhance their learning experience.

---

## 1. Delete Conversation

**Purpose:** Remove old or unwanted conversations to keep your chat history organized.

**When to use:**
- Clean up temporary explorations
- Remove duplicate conversations
- Organize by keeping only useful discussions
- Free up space

**API Endpoint:**
```
DELETE /api/chat/conversations/{conversation_id}
```

**Example Usage:**
```typescript
// Delete a conversation
const response = await fetch('/api/chat/conversations/abc-123-def', {
  method: 'DELETE',
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const result = await response.json();
// { "status": "success", "message": "Conversation deleted" }
```

**Response:**
```json
{
  "status": "success",
  "message": "Conversation deleted"
}
```

**Status Codes:**
- `200` - Successfully deleted
- `401` - Unauthorized (need login)
- `500` - Server error

**Benefits:**
- 📋 Keep history organized
- 🧹 Reduce clutter
- 🔒 Privacy control
- 💾 Reclaim storage space

---

## 2. Edit Conversation Title

**Purpose:** Rename auto-generated titles to something more meaningful.

**Why it matters:**
- Auto-generated titles might not capture the full discussion
- Custom names help organize by topic
- Easier to find specific conversations later
- Personal learning system

**API Endpoint:**
```
PATCH /api/chat/conversations/{conversation_id}
```

**Request Body:**
```json
{
  "title": "My Custom Title"
}
```

**Example Usage:**
```typescript
// Rename a conversation
const response = await fetch('/api/chat/conversations/abc-123-def', {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    title: "Photosynthesis - Study Notes"
  })
});

const result = await response.json();
// { "status": "success", "title": "Photosynthesis - Study Notes" }
```

**Response:**
```json
{
  "status": "success",
  "conversation_id": "abc-123-def",
  "title": "Photosynthesis - Study Notes"
}
```

**Title Examples:**
```
Auto-generated: "What is photosynthesis?"
Custom: "Photosynthesis - Study Notes"

Auto-generated: "Cellular Respiration Study Help"
Custom: "Bio Final: Cellular Respiration Review"

Auto-generated: "Explain Newton's first law"
Custom: "Physics - Newton's Laws (Exam Prep)"
```

**Benefits:**
- 📚 Better organization
- 📝 Meaningful titles
- 🔍 Easier searching
- 🎯 Personal learning system

---

## 3. Search Conversations

**Purpose:** Find conversations by title or content using full-text search.

**Use Cases:**
- Find previous explanations of similar topics
- Locate specific discussions
- Review related learning
- Avoid repeating questions
- Build on previous understanding

**API Endpoint:**
```
GET /api/chat/conversations/search?q=<search_query>
```

**Query Parameters:**
- `q` (required) - Search query string

**Example Usage:**
```typescript
// Search for conversations about photosynthesis
const response = await fetch(
  '/api/chat/conversations/search?q=photosynthesis',
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

const result = await response.json();
```

**Response:**
```json
{
  "query": "photosynthesis",
  "total_results": 3,
  "results": [
    {
      "conversation_id": "uuid-1",
      "title": "Photosynthesis - Study Notes",
      "last_message": "The light-dependent reactions occur...",
      "match_context": "Title contains 'photosynthesis'",
      "created_at": "2026-01-17T09:00:00"
    },
    {
      "conversation_id": "uuid-2",
      "title": "Biology Final Prep",
      "last_message": "Photosynthesis involves the conversion of light energy...",
      "match_context": "Message contains 'photosynthesis'",
      "created_at": "2026-01-16T14:00:00"
    }
  ]
}
```

**Search Examples:**
```
Query: "photosynthesis"
→ Finds all conversations about photosynthesis

Query: "exam"
→ Finds all conversations tagged as exam prep

Query: "DNA replication"
→ Finds discussions about DNA replication

Query: "biology"
→ Finds all biology-related conversations
```

**Benefits:**
- ⚡ Quickly find past discussions
- ♻️ Avoid repeating questions
- 🔄 Build on previous learning
- 🎯 Efficient knowledge retrieval

---

## 4. Message Feedback

**Purpose:** Rate each AI response as helpful or not helpful to improve learning.

**Why it matters:**
- Helps identify which responses help you learn best
- Creates personal learning analytics
- Improves future responses based on your needs
- Tracks your understanding journey
- Provides learning insights

**API Endpoint:**
```
POST /api/chat/conversations/{conversation_id}/messages/{message_id}/feedback
```

**Path Parameters:**
- `conversation_id` (required) - UUID of the conversation
- `message_id` (required) - ID of the specific message

**Request Body:**
```json
{
  "feedback": "helpful"
}
```

**Feedback Values:**
- `"helpful"` - Response was useful and clear
- `"not_helpful"` - Response was unclear or unhelpful

**Example Usage:**
```typescript
// Mark a response as helpful
const response = await fetch(
  '/api/chat/conversations/abc-123-def/messages/msg-456/feedback',
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      feedback: "helpful"
    })
  }
);

const result = await response.json();
// { "status": "success", "message": "Feedback saved" }
```

**Response:**
```json
{
  "status": "success",
  "message": "Feedback saved"
}
```

**Example Scenario:**
```typescript
// Student reads AI response about photosynthesis
// If clear and helpful:
POST /feedback { "feedback": "helpful" }

// If confusing or inaccurate:
POST /feedback { "feedback": "not_helpful" }
```

**Feedback Tracking:**
```
Over time, you can see:
- Which response types help you most
- Your understanding progression
- Topics that need more review
- Most effective explanations
```

**Benefits:**
- 📊 Track what helps you learn
- 📈 Identify knowledge gaps
- 🎯 Guide future study plans
- 📉 Monitor improvement over time
- 💡 Personal learning analytics

---

## 5. Export Conversation as PDF

**Purpose:** Download conversations as formatted PDF files for offline study.

**Use Cases:**
- Print for physical study materials
- Share with study group members
- Offline studying (no internet required)
- Portfolio documentation
- Exam preparation materials
- Reference materials library

**API Endpoint:**
```
GET /api/admin/conversations/{conversation_id}/export?format=pdf
```

**Query Parameters:**
- `format` (optional) - `pdf` (default) or `json`

**Supported Formats:**
- `pdf` - Professional formatted PDF (default)
- `json` - Structured data format

**Example Usage:**
```typescript
// Export as PDF
async function exportConversation(conversationId) {
  const response = await fetch(
    `/api/admin/conversations/${conversationId}/export?format=pdf`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  
  const blob = await response.blob();
  
  // Create download link
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `photosynthesis-notes.pdf`;
  document.body.appendChild(a);
  a.click();
  window.URL.revokeObjectURL(url);
}

// Call it
exportConversation('abc-123-def');
```

**PDF Format:**
The exported PDF includes:
- ✅ Conversation title (large header)
- ✅ Creation date/timestamp
- ✅ All messages (user questions & AI responses)
- ✅ Source citations (which PDFs were used)
- ✅ Relevance scores for sources
- ✅ Professional formatting for printing
- ✅ Page breaks for readability

**PDF Structure Example:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    Photosynthesis - Study Notes
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Created: January 17, 2026 at 9:00 AM

─────────────────────────────────────────

USER:
What is photosynthesis?

ASSISTANT:
Photosynthesis is the biological process by which
plants convert light energy into chemical energy
stored in glucose molecules. This process occurs
primarily in the chloroplasts of plant cells...

Sources:
  • biology_notes.pdf (Relevance: 0.92)
  • textbook_chapter3.pdf (Relevance: 0.88)

─────────────────────────────────────────

USER:
How does it relate to cellular respiration?

ASSISTANT:
Photosynthesis and cellular respiration are
complementary processes...

Sources:
  • biology_notes.pdf (Relevance: 0.95)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Export as JSON:**
```typescript
// Get structured data instead of PDF
const response = await fetch(
  `/api/admin/conversations/${id}/export?format=json`,
  {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  }
);

const data = await response.json();
// Contains full conversation metadata and messages
```

**JSON Response:**
```json
{
  "conversation_id": "abc-123-def",
  "title": "Photosynthesis - Study Notes",
  "created_at": "2026-01-17T09:00:00",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "What is photosynthesis?",
      "timestamp": "2026-01-17T09:05:00"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Photosynthesis is the biological process...",
      "sources": [
        {
          "filename": "biology_notes.pdf",
          "relevance_score": 0.92
        }
      ],
      "timestamp": "2026-01-17T09:06:00"
    }
  ]
}
```

**Use Cases in Detail:**

**1. Print Study Material**
```
→ Export PDF
→ Print at home or campus
→ Annotate with highlighter/pen
→ Use as handout for study group
```

**2. Share with Classmates**
```
→ Export PDF
→ Email or upload to study group chat
→ Everyone has reference material
→ Build collaborative study docs
```

**3. Offline Study**
```
→ Export PDF before class
→ Read in airplane/train (no WiFi)
→ Prepare for exams offline
→ Review during breaks
```

**4. Build Study Library**
```
→ Export all conversations at end of semester
→ Organize PDFs by topic
→ Create study guide collection
→ Reference for future courses
```

**5. Portfolio Documentation**
```
→ Export best conversations
→ Show learning progression
→ Portfolio of study work
→ Academic documentation
```

**Benefits:**
- 🖨️ Printable study materials
- 📤 Easy sharing with classmates
- 📱 Offline access (no internet)
- 📚 Build study library
- 🎓 Professional documentation
- 💾 Permanent reference materials

---

## Usage Workflow Example

Here's a typical student workflow using all 5 features:

### Day 1: Initial Study Session
```typescript
// Create conversation
POST /api/chat/ {
  message: "Explain photosynthesis",
  prompt_type: "explanation"
}
// Returns: conversation_id = "abc-123"
```

### Day 1: Organizing
```typescript
// Auto-generated title wasn't great
PATCH /api/chat/conversations/abc-123 {
  title: "Photosynthesis - Light & Dark Reactions"
}
```

### Day 1: Learning
```typescript
// Rate responses
POST /api/chat/conversations/abc-123/messages/msg-1/feedback {
  feedback: "helpful"
}
```

### Day 2: Review
```typescript
// Search for previous photosynthesis discussion
GET /api/chat/conversations/search?q=photosynthesis
// Returns: found abc-123
```

### Day 2: Export
```typescript
// Print for exam prep
GET /api/admin/conversations/abc-123/export?format=pdf
// Downloads: "Photosynthesis - Light & Dark Reactions.pdf"
```

### Day 3: Cleanup
```typescript
// Delete duplicate/low-quality conversation
DELETE /api/chat/conversations/xyz-789
```

---

## Integration Guide

### Frontend Button Examples

**Delete Button:**
```typescript
<button onClick={() => deleteConversation(id)}>🗑️ Delete</button>

async function deleteConversation(id: string) {
  await fetch(`/api/chat/conversations/${id}`, {
    method: 'DELETE',
    headers: { 'Authorization': `Bearer ${token}` }
  });
}
```

**Edit Title:**
```typescript
<input 
  value={title}
  onBlur={() => updateTitle(id, title)}
/>

async function updateTitle(id: string, newTitle: string) {
  await fetch(`/api/chat/conversations/${id}`, {
    method: 'PATCH',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ title: newTitle })
  });
}
```

**Search:**
```typescript
<input placeholder="Search conversations..." onChange={(e) => search(e.target.value)} />

async function search(query: string) {
  const res = await fetch(
    `/api/chat/conversations/search?q=${encodeURIComponent(query)}`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  return res.json();
}
```

**Feedback Buttons:**
```typescript
<button onClick={() => feedback(msgId, 'helpful')}>👍 Helpful</button>
<button onClick={() => feedback(msgId, 'not_helpful')}>👎 Not Helpful</button>

async function feedback(msgId: string, type: string) {
  await fetch(
    `/api/chat/conversations/${conversationId}/messages/${msgId}/feedback`,
    {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ feedback: type })
    }
  );
}
```

**Export:**
```typescript
<button onClick={() => exportPDF(id)}>📥 Export PDF</button>

async function exportPDF(id: string) {
  const res = await fetch(
    `/api/admin/conversations/${id}/export?format=pdf`,
    { headers: { 'Authorization': `Bearer ${token}` } }
  );
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `conversation.pdf`;
  a.click();
}
```

---

## Summary

These 5 features work together to create a complete personal learning management system:

| Feature | Purpose | When to Use |
|---------|---------|-----------|
| **Delete** | Remove conversations | Cleanup, organization |
| **Edit Title** | Organize with custom names | After creating conversation |
| **Search** | Find past discussions | Review, avoid repeating |
| **Feedback** | Rate responses | During/after learning |
| **Export PDF** | Study offline/share | Exam prep, printing |

Together, they transform NoteGPT from a simple chatbot into a complete personal learning assistant! 🎓📚

