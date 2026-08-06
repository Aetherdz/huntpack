## Report Templates بالعربية

### قالب ثغرة IDOR
```markdown
# [IDOR]: الوصول غير المصرح به لبيانات المستخدمين في [endpoint]

**الهدف:** domain.com
**البرنامج:** [HackerOne/Bugcrowd/خاص]
**التاريخ:** YYYY-MM-DD
**الشدة:** عالية (High)
**CVSS 3.1:** 7.5 (AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)

## الملخص
[ثغرة IDOR في endpoint تسمح لأي مستخدم بمشاهدة بيانات أي مستخدم آخر]

## النطاق
- داخل النطاق: [endpoints]
- خارج النطاق: [ما لم يتم اختباره]

## التفاصيل التقنية
### الـ Endpoint المتأثر
`GET /api/v1/users/{user_id}`

### سبب الثغرة
[الـ endpoint لا يتحقق من ملكية المستخدم للمورد المطلوب]

### خطوات إعادة الإنتاج
1. سجّل مستخدم A واحصل على JWT
2. سجّل مستخدم B واحصل على JWT
3. استخدم JWT الخاص بـ B للوصول إلى /api/v1/users/A
4. لاحظ عودة بيانات A (بريد إلكتروني، دور، إلخ)

### الدليل
\`\`\`bash
curl -s "https://target.com/api/v1/users/1" \
   -H "Authorization: Bearer $JWT_B" | jq .
\`\`\`

### الأثر التجاري
- **كشف بيانات**: 1000+ مستخدم
- **خطر مالي**: [وصف]
- **الامتثال**: violation محتمل لـ GDPR

### الإصلاح
إضافة التحقق من المالك قبل إعادة البيانات:
\`\`\`python
def get_user(user_id, current_user):
    resource = User.query.get(user_id)
    if current_user.role != 'admin' and resource.id != current_user.id:
        return abort(403)
    return resource
\`\`\`
```

### قالب ثغرة Business Logic
```markdown
# [Business Logic]: [تجاوز/التلاعب بـ] في [الميزة]

**الهدف:** domain.com
**الشدة:** عالية (High)
**CVSS 3.1:** 7.7 (AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:N)

## الملخص
[وصف الثغرة المنطقية وتأثيرها]

## الخطوات
1. [خطوة 1]
2. [خطوة 2]
3. [لاحظ النتيجة غير المتوقعة]

## تحليل السبب
[الـ business logic لا تتعامل مع حالة استخدام الميزة بطريقة غير متوقعة]

## الأثر
[مباشر على الإيرادات/الصلاحيات/البيانات]
```

---

