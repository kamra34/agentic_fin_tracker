# Performance Analysis

## 🔍 Problem Identified

Your dashboard is loading slowly due to **network latency to the Raspberry Pi PostgreSQL database**.

### Key Findings:

1. **User Lookup Query is the Bottleneck**
   - Every API endpoint calls `get_current_user()` which queries the database
   - Each query takes: **120-437ms** (!!!)
   - This happens on EVERY request, even concurrent ones

2. **Example from Logs:**
   ```
   SLOW QUERY (437.57ms): SELECT users.id, users.email, users.hashed_password...
   SLOW QUERY (117.77ms): SELECT users.id, users.email, users.hashed_password...
   SLOW QUERY (131.07ms): SELECT users.id, users.email, users.hashed_password...
   ```

3. **Multiple Concurrent Requests Compound the Problem:**
   - Dashboard loads 4+ APIs simultaneously
   - Each waits for user auth → **14+ seconds total**

### Why This Happens:

1. **Network Latency**: Raspberry Pi is on local network, not localhost
2. **No Caching**: User is fetched fresh from DB on every request
3. **No Connection Pooling Optimization**: Default pool settings

---

## 🚀 Solutions (Ordered by Impact)

### 1. **Cache User Lookups** ⭐ HIGHEST IMPACT
Add Redis or in-memory caching for user objects:
- Cache user for 5-10 minutes after first lookup
- Reduce 437ms → ~5ms for cached hits

### 2. **Optimize Database Connection**
- Add database indexes on `users.id` (if not exists)
- Increase connection pool size
- Use connection pooling properly

### 3. **Network Optimization**
- Ensure Raspberry Pi and your machine are on same subnet
- Check network switch/router performance
- Consider running PostgreSQL locally for development

### 4. **Batch API Calls**
- Create a single `/api/dashboard/full` endpoint
- Returns all data in one request
- Reduces round trips from 4+ → 1

### 5. **JWT Optimization**
- Store user ID in JWT payload
- Skip database lookup for basic auth checks
- Only query DB when user details are actually needed

---

## 📊 Actual Performance (from your logs):

### First Load (with React StrictMode doubling calls):
| Endpoint | Total Time | Server Time | Observations |
|----------|-----------|-------------|--------------|
| `/api/auth/login` | 2,253ms | 1,909ms | Login is slow! |
| `/api/dashboard/stats` | 3,104ms | 3,065ms | Heavy queries |
| `/api/auth/me` | 4,713ms | 3,089ms | User lookup slow |
| `/api/incomes/templates` | 4,716ms | 4,680ms | **VERY SLOW** |
| `/api/expenses/templates` | 4,719ms | 3,094ms | Slow queries |

### Second Load (duplicate calls from StrictMode):
| Endpoint | Total Time | Server Time | Impact |
|----------|-----------|-------------|--------|
| `/api/dashboard/stats` | 5,096ms | 1,992ms | Queued behind first calls |
| `/api/auth/me` | 5,692ms | 975ms | Better (cached?) |
| `/api/expenses/templates` | 5,751ms | 658ms | **Much faster!** |
| `/api/incomes/templates` | 5,823ms | 1,100ms | Queued |

**Root Cause**:
1. Raspberry Pi PostgreSQL is **3-4 seconds per request** (network + query time)
2. React StrictMode causes **duplicate API calls** in development
3. No caching means every request hits the database

---

## 🛠️ Debug Tools Added:

### Backend (`main.py` + `database.py`):
- ⏱️ Request timing middleware
- 🐌 Slow query logging (>100ms)
- ⚡ Query timing for all DB operations

### Frontend (`api.js`):
- 🚀 API request start logging
- ✅ Response timing with server time comparison
- 🐌 Slow API call warnings (>1000ms)

Check your browser console and backend logs to see detailed timing!
