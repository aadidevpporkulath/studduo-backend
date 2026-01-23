# Features Overview

Complete guide to all NoteGPT features and capabilities.

## 🎯 Core Features

### 1. Multi-Domain RAG Chat

**What it does:**
Answers questions using your PDF course materials from any subject.

**How it works:**

- Upload PDFs to `./knowledge/` folder
- Ingest documents (creates embeddings)
- Ask questions - AI retrieves relevant chunks
- Generates teaching-focused responses

**Benefits:**

- Works with any subject (math, history, biology, etc.)
- No need to retrain models
- Add/remove subjects anytime
- Cites sources with each answer

**Example:**

```json
{
  "message": "Explain photosynthesis",
  "prompt_type": "explanation"
}

Response includes:
- Detailed explanation
- Sources (which PDFs/pages)
- Follow-up questions
```

---

### 2. Six Prompt Types

**What it does:**
Provides different teaching response styles for different learning needs.

**Available Types:**

#### **Explanation** (Default)

Detailed teaching explanations with examples.

```json
{
  "message": "What is gravity?",
  "prompt_type": "explanation"
}
```

**Response format:**

- Clear answer upfront
- Why and how it works
- Real-world examples
- Encouraging tone

---

#### **Plan**

Step-by-step procedures and workflows.

```json
{
  "message": "How do I solve a quadratic equation?",
  "prompt_type": "plan"
}
```

**Response format:**

- Numbered steps
- What happens at each step
- Practical tips
- Common mistakes
- Time/difficulty estimates

---

#### **Example**

Worked examples with solutions.

```json
{
  "message": "Show me force calculations",
  "prompt_type": "example"
}
```

**Response format:**

- Simple example first
- Step-by-step walkthrough
- Multiple examples (easy → complex)
- Key patterns highlighted
- Formulas included

---

#### **Summary**

Quick reference and revision.

```json
{
  "message": "Summarize the water cycle",
  "prompt_type": "summary"
}
```

**Response format:**

- 2-3 sentence overview
- 3-5 bullet points
- One analogy
- Practical applications
- Follow-up topic suggestion

---

#### **Problem Solving**

Guides to solve problems.

```json
{
  "message": "How do I solve this derivative?",
  "prompt_type": "problem_solving"
}
```

**Response format:**

- Problem acknowledgment
- Break into parts
- Methodology explanation
- Step-by-step solution
- Why it works
- Alternative approaches

---

#### **Quiz**

Self-assessment questions.

```json
{
  "message": "Quiz me on World War II",
  "prompt_type": "quiz"
}
```

**Response format:**

- 3-4 questions
- Varying difficulty
- Multiple choice or short answer
- Answer explanations
- Review suggestions

---

### 3. Temporary Conversations

**What it does:**
Quick queries that aren't saved to the database.

**Use Cases:**

- Quick lookups
- Testing understanding
- Exploring topics
- Practice quizzes
- Experimenting

**How to use:**

```json
{
  "message": "Quick question about DNA",
  "is_temporary": true
}
```

**Benefits:**

- Don't clutter conversation history
- Faster (no database writes)
- Perfect for exploration
- No permanent record

**Limitations:**

- Can't resume temporary conversations
- No history available
- Each query is standalone

**Example:**

```typescript
// Quick quiz (don't save)
await chat({
  message: "Quiz me on algebra",
  prompt_type: "quiz",
  is_temporary: true
});

// Regular conversation (save)
await chat({
  message: "Explain algebra fundamentals",
  prompt_type: "explanation",
  is_temporary: false
});
```

---

### 4. Conversation History & Context

**What it does:**
Maintains conversation context across multiple messages.

**Features:**

- Auto-saves all messages
- Loads last 4 exchanges for context
- Continue conversations anytime
- Retrieve full message history

**How it works:**

```json
// First message
POST /api/chat/
{
  "message": "What is DNA?",
  "conversation_id": null
}

Response: { "conversation_id": "abc-123" }

// Follow-up (uses context)
POST /api/chat/
{
  "message": "How is it replicated?",
  "conversation_id": "abc-123",
  "include_history": true
}
```

**Benefits:**

- Natural conversation flow
- AI understands context
- Resume anytime
- Full conversation retrieval

---

### 5. Auto-Generated Titles

**What it does:**
Automatically creates conversation titles from the first message.

**How it works:**

1. You send first message
2. If ≤ 50 characters: uses message as title
3. If > 50 characters: LLM generates 3-5 word title
4. Falls back to truncation if generation fails

**Examples:**

``` txt
Message: "What is photosynthesis?"
Title: "What is photosynthesis?"

Message: "Can you explain the complete process of photosynthesis including light and dark reactions?"
Title: "Photosynthesis Process Overview"

Message: "I'm studying for my biology exam tomorrow and need help understanding cellular respiration"
Title: "Cellular Respiration Study Help"
```

**Benefits:**

- Easy to identify conversations
- No manual naming needed
- Descriptive and concise
- Searchable

---

### 6. Embedding Cache

**What it does:**
Caches embeddings for repeated queries to improve performance.

**Performance:**

- **Cache hit:** ~0.001s (instant)
- **Cache miss:** ~0.5-2s (generate embedding)
- **Speedup:** 500-2000x faster

**How it works:**

1. Query arrives: "What is DNA?"
2. Generate MD5 hash of query
3. Check cache for hash
4. If found: use cached embedding
5. If not: generate, cache, and use

**Cache management:**

- Max 1000 entries
- LRU-style pruning
- Automatic cleanup
- In-memory storage

**Example:**

``` txt
Query 1: "What is DNA?"          → Generate embedding (1.2s)
Query 2: "What is DNA?"          → Cache hit! (0.001s)
Query 3: "How is DNA replicated?" → Generate embedding (1.1s)
Query 4: "What is DNA?"          → Cache hit! (0.001s)
```

**Benefits:**

- Dramatically faster responses
- Lower API costs (local embeddings)
- Better user experience
- Automatic optimization

---

### 7. Source Citations

**What it does:**
Shows which documents were used to answer each question.

**Format:**

```json
{
  "sources": [
    {
      "source": "biology_notes.pdf",
      "chunk_id": 5,
      "relevance_score": 0.92
    },
    {
      "source": "textbook_chapter3.pdf",
      "chunk_id": 12,
      "relevance_score": 0.88
    }
  ]
}
```

**Benefits:**

- Verify information source
- Check material coverage
- Build trust
- Enable further reading

---

### 8. Follow-Up Questions

**What it does:**
Suggests relevant follow-up questions after each response.

**How it works:**

- LLM analyzes your question and its response
- Generates 2 related questions
- Questions build on what was explained
- Encourages deeper exploration

**Example:**

```json
{
  "message": "What is photosynthesis?",
  "follow_up_questions": [
    "What are the stages of photosynthesis?",
    "How does light intensity affect photosynthesis?"
  ]
}
```

**Benefits:**

- Guided learning path
- Discover related topics
- Deepen understanding
- Natural conversation flow

---

### 9. Pagination Support

**What it does:**
Efficiently handles large conversation histories.

**Parameters:**

- `offset` - Skip N conversations
- `limit` - Max conversations to return (max 100)

**Use cases:**

```typescript
// Load first page
GET /api/chat/conversations?offset=0&limit=20

// Load next page
GET /api/chat/conversations?offset=20&limit=20

// Infinite scroll
const loadMore = (page) => {
  return fetch(`/api/chat/conversations?offset=${page * 20}&limit=20`);
};
```

**Benefits:**

- Fast initial load
- Handle 1000+ conversations
- Support infinite scroll
- Reduced memory usage

---

### 10. Multi-User Support

**What it does:**
Each user has isolated conversations and data.

**Features:**

- Firebase authentication
- User-specific conversations
- Data isolation
- Secure access control

**How it works:**

```
User A:
  - Conversations: A1, A2, A3
  - Can only see/access own data

User B:
  - Conversations: B1, B2, B3
  - Can only see/access own data
```

---

## 🎓 Learning Scenarios

### Scenario 1: Study Session

```typescript
// Understanding concept
POST /api/chat/ {
  message: "Explain Newton's laws",
  prompt_type: "explanation"
}

// Get examples
POST /api/chat/ {
  message: "Show me examples",
  conversation_id: "same-id",
  prompt_type: "example"
}

// Test knowledge
POST /api/chat/ {
  message: "Quiz me",
  conversation_id: "same-id",
  prompt_type: "quiz"
}
```

---

### Scenario 2: Quick Lookup

```typescript
// Quick summary (don't save)
POST /api/chat/ {
  message: "Summarize mitosis",
  prompt_type: "summary",
  is_temporary: true
}
```

---

### Scenario 3: Problem Solving

```typescript
// Get solution guide
POST /api/chat/ {
  message: "How do I solve x² + 5x + 6 = 0?",
  prompt_type: "problem_solving"
}

// Get step-by-step plan
POST /api/chat/ {
  message: "Show me the steps",
  conversation_id: "same-id",
  prompt_type: "plan"
}
```

---

### Scenario 4: Exam Preparation

```typescript
// Study main topics
POST /api/chat/ {
  message: "Explain key chemistry concepts",
  prompt_type: "explanation"
}

// Get summaries
POST /api/chat/ {
  message: "Summarize chemical bonding",
  prompt_type: "summary",
  is_temporary: true  // Many quick summaries
}

// Practice quizzes
POST /api/chat/ {
  message: "Quiz me on organic chemistry",
  prompt_type: "quiz",
  is_temporary: true
}
```

---

## 🔧 Configuration Options

### Adjustable Parameters

**RAG Settings** (`config.py`):

```python
chunk_size = 1000          # Characters per chunk
chunk_overlap = 200        # Overlap between chunks
top_k_results = 5          # Documents retrieved per query
```

**LLM Settings** (`config.py`):

```python
model_name = "gemini-2.5-flash"
temperature = 0.7          # Creativity (0-1)
max_tokens = 2048          # Max response length
```

**Cache Settings** (in code):

```python
max_cache_size = 1000      # Max cached embeddings
```

---

## 📊 Feature Comparison

| Feature | Regular Chat | Temporary Chat |
|---------|-------------|----------------|
| Saved to DB | ✅ Yes | ❌ No |
| Has History | ✅ Yes | ❌ No |
| Can Resume | ✅ Yes | ❌ No |
| In List | ✅ Yes | ❌ No |
| Has Title | ✅ Yes | ❌ No |
| Prompt Types | ✅ All 6 | ✅ All 6 |
| Follow-ups | ✅ Yes | ✅ Yes |
| Sources | ✅ Yes | ✅ Yes |
| Performance | Fast | Faster |

---

## 🚀 Performance Features

1. **Embedding Cache** - 500x faster repeated queries
2. **Async Operations** - Non-blocking I/O
3. **Pagination** - Efficient data loading
4. **Batch Processing** - Optimized document ingestion
5. **Local Embeddings** - No external API calls

---

## 🔒 Security Features

1. **Firebase Auth** - Secure user authentication
2. **User Isolation** - Data privacy
3. **CORS** - Restricted origins
4. **Token Verification** - Every request validated

---

## Next Steps

- See [API Overview](API_OVERVIEW.md) for endpoint details
- Read [Prompt Types](PROMPT_TYPES.md) for detailed prompt documentation
- Check [Frontend Integration](FRONTEND_INTEGRATION.md) for implementation examples
- Review [Architecture](ARCHITECTURE.md) for system design
