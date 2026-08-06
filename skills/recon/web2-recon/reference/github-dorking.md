## GITHUB DORKING FOR TARGET

> **⚙️ Tool note:** if `tools/GitDorker/GitDorker.py` isn't installed, use `trufflehog github --org=TARGET_ORG --only-verified`, `gitleaks`, or GitHub code search directly (`https://github.com/search?q=org:TARGET+password&type=code`). Also try `github-subdomains -d TARGET -t $GH_TOKEN` for hostnames in code.

```bash
# Search GitHub for hardcoded secrets before hunting the app
TARGET_ORG="TargetOrgName"  # Check their GitHub org

# Useful dorks (search on github.com):
# org:TARGET_ORG password
# org:TARGET_ORG api_key
# org:TARGET_ORG "Authorization: Bearer"
# org:TARGET_ORG .env
# org:TARGET_ORG "BEGIN RSA PRIVATE KEY"

# CLI with gh (GitHub CLI):
gh search code "api_key" --owner "$TARGET_ORG" --json path,repository 2>/dev/null | jq '.'
gh search code "password" --owner "$TARGET_ORG" --json path,repository 2>/dev/null | head -20

# GitDorker (if installed):
python3 ~/tools/GitDorker/GitDorker.py -t GITHUB_TOKEN -d ~/tools/GitDorker/Dorks/alldorksv3 -q "$TARGET" -org
```
