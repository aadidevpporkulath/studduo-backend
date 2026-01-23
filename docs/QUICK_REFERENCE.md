# 5 Student-Focused Features - Quick Reference

## 🎯 Quick API Reference Card

All endpoints require Firebase authentication token in `Authorization: Bearer {token}` header.

---

## 1️⃣ DELETE CONVERSATION

**Remove conversations to keep organized**

```
DELETE /api/chat/conversations/{conversation_id}
```

**Response:**
```json
{ "status": "success", "message": "Conversation deleted" }
```

**Example (JavaScript):**
```javascript
await fetch(`/api/chat/conversations/${id}`, {
  method: 'DELETE',
  headers: { 'Authorization': `Bearer ${token}` }
});
```

---

## 2️⃣ EDIT CONVERSATION TITLE

**Rename conversations for better organization**

```
PATCH /api/chat/conversations/{conversation_id}
```

**Body:**
```json
{ "title": "My Custom Title" }
```

**Response:**
```json
{ "status": "success", "conversation_id": "abc-123", "title": "My Custom Title" }
```

**Example (JavaScript):**
```javascript
await fetch(`/api/chat/conversations/${id}`, {
  method: 'PATCH',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({ title: "New Title" })
});
```

---

## 3️⃣ SEARCH CONVERSATIONS

**Find past discussions by title**

```
GET /api/chat/conversations/search?q={search_query}
```

**Response:**
```json
{
  "query": "photosynthesis",
  "total_results": 3,
  "results": [
    {
      "conversation_id": "uuid-1",
      "title": "Photosynthesis Basics",
      "last_message": "...",
      "created_at": "2026-01-17T09:00:00"
    }
  ]
}
```

**Example (JavaScript):**
```javascript
const res = await fetch(
  `/api/chat/conversations/search?q=${encodeURIComponent('photosynthesis')}`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const data = await res.json();
```

---

## 4️⃣ MESSAGE FEEDBACK

**Rate responses as helpful or not helpful**

```
POST /api/chat/conversations/{conversation_id}/messages/{message_id}/feedback
```

**Body:**
```json
{ "feedback": "helpful" }
```

Valid values: `"helpful"` or `"not_helpful"`

**Response:**
```json
{ "status": "success", "message": "Feedback saved" }
```

**Example (JavaScript):**
```javascript
await fetch(
  `/api/chat/conversations/${convId}/messages/${msgId}/feedback`,
  {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ feedback: 'helpful' })
  }
);
```

---

## 5️⃣ EXPORT AS PDF

**Download conversations for offline study**

```
GET /api/admin/conversations/{conversation_id}/export?format=pdf
```

**Formats:**
- `?format=pdf` (default) - Professional PDF
- `?format=json` - Structured JSON data

**Response:**
- **PDF:** File download (application/pdf)
- **JSON:** Full conversation object

**Example (JavaScript - PDF Download):**
```javascript
const res = await fetch(
  `/api/admin/conversations/${id}/export?format=pdf`,
  { headers: { 'Authorization': `Bearer ${token}` } }
);
const blob = await res.blob();

// Create download
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = 'conversation.pdf';
a.click();
```

---

## ⚙️ HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | ✅ Success |
| 400 | ❌ Bad request (invalid data) |
| 401 | 🔒 Unauthorized (invalid/missing token) |
| 404 | 🔍 Not found (conversation doesn't exist) |
| 500 | ⚠️ Server error |

---

## 🔐 Authentication

All endpoints require:
```
Authorization: Bearer {firebase_id_token}
```

Get token in frontend:
```javascript
import { getAuth } from 'firebase/auth';

const auth = getAuth();
const token = await auth.currentUser.getIdToken();
```

---

## 📱 Frontend Integration Pattern

```typescript
// Create a hook for each feature
export function useDeleteConversation() {
  return async (id: string, token: string) => {
    const res = await fetch(`/api/chat/conversations/${id}`, {
      method: 'DELETE',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    return res.json();
  };
}

export function useEditTitle() {
  return async (id: string, title: string, token: string) => {
    const res = await fetch(`/api/chat/conversations/${id}`, {
      method: 'PATCH',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ title })
    });
    return res.json();
  };
}

// Use in components
function ConversationItem({ id, title, token }) {
  const deleteConv = useDeleteConversation();
  const editTitle = useEditTitle();
  
  return (
    <div>
      <input value={title} onBlur={() => editTitle(id, title, token)} />
      <button onClick={() => deleteConv(id, token)}>Delete</button>
    </div>
  );
}
```

---

## 🧪 Testing with cURL

```bash
# Search conversations
curl -X GET "http://localhost:8000/api/chat/conversations/search?q=photosynthesis" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Update title
curl -X PATCH "http://localhost:8000/api/chat/conversations/CONV_ID" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title":"New Title"}'

# Add feedback
curl -X POST "http://localhost:8000/api/chat/conversations/CONV_ID/messages/MSG_ID/feedback" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"feedback":"helpful"}'

# Export PDF
curl -X GET "http://localhost:8000/api/admin/conversations/CONV_ID/export?format=pdf" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o conversation.pdf

# Delete conversation
curl -X DELETE "http://localhost:8000/api/chat/conversations/CONV_ID" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📚 Documentation

For detailed documentation:
- **API Details:** See `/docs/API_OVERVIEW.md`
- **Feature Guide:** See `/docs/STUDENT_FEATURES.md`
- **Frontend Examples:** See `/docs/FRONTEND_INTEGRATION.md`
- **Full Docs:** See `/docs/README.md`

---

## 🚀 Ready to Implement?

1. Get Firebase token from authenticated user
2. Choose endpoint from above
3. Make HTTP request with proper headers
4. Handle response (200 success, others are errors)
5. Update UI accordingly

**That's it!** 🎉

