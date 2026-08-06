## 7. SOCIAL MEDIA

### Signature Assets
- User profiles, personal data
- Posts, messages, stories
- Connections, followers, friends
- Private messages, DMs
- Location data, check-ins
- Ad accounts, targeting data

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| User | Post, follow, message | DM IDOR |
| Verified | Additional features | Verification bypass |
| Moderator | Content moderation | Unmoderated access |
| Advertiser | Ads management | Data leak |

### Priority Attack Surface

```
1. DM / PRIVATE MESSAGE IDOR ← HIGHEST VALUE
   GET  /api/messages/{id}               → sequential message IDs
   GET  /api/conversations/{id}           → access others' conversations
   GET  /api/messages?userId={target}     → enumerate messages by userId
   Test: User A sends DM to User B, check if User C can access

2. FOLLOW/CONNECTION RACE
   POST /api/follow/{userId}              → race (force follow)
   POST /api/unfollow/{userId}            → unblock by race
   POST /api/connect/{userId}             → force connection
   Test: 100 concurrent follow requests on same user

3. PRIVACY SETTING BYPASS
   GET  /api/profile/{userId}             → access private profile
   GET  /api/photos/{id}                  → access private photos
   GET  /api/stories/{id}                 → view expired stories
   Test: User A sets profile to private, User B tries to view

4. POST / COMMENT IDOR
   DELETE /api/posts/{id}                 → delete others' posts
   PUT    /api/posts/{id}                 → edit others' posts
   DELETE /api/comments/{id}              → delete others' comments
   Test: check authorization on all CRUD operations

5. EMAIL / PHONE ENUMERATION
   POST /api/auth/check-email             → check if email registered
   POST /api/auth/check-phone             → check if phone registered
   POST /api/users/search                 → search by email/phone
   Test: LinkedIn-style enumeration
```

### Top Attack Chains
```
1. [Critical] DM IDOR → Read All DMs → Extract Secrets/Blackmail → Extortion
2. [High]      Email Enumeration → Build Targeted List → Password Reset Attack → ATO
3. [High]      Follow Race → Force 100K Followers → Fake Influencer → Scam Brands
4. [Medium]    Privacy Bypass → View Private Photos → Dox Target
5. [Medium]    Post IDOR → Delete Competitor's Viral Post → Reputation Damage
```

### Real H1 Examples
- LinkedIn: IDOR on private messages (#1734639)
- Pixiv: IDOR on private illustrations (#3100570)
- Pixiv: IDOR on bookmarks/comments (#2541962)

---

