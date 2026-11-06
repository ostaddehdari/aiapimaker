# Django API — قرارداد مقدماتی (Stage 20 تثبیت می‌شود)

**API Base:** `https://srun.ir/aiapimaker/api/v1/`  
**Frontend:** `https://srun.ir/aiapimaker/`  
**امکان اتصال‌ها:** وابسته به Provider Capability و مجوز اتصال؛ نه تضمین همه سرویس‌ها در روز اول.

## مسیرهای منتخب
| Method | Path | کاربرد |
|---|---|---|
| POST | `auth/login/` | ورود امن در React، Cookie Session و CSRF |
| POST | `auth/logout/` | خروج |
| GET | `auth/me/` | کاربر و نقش |
| GET/POST | `providers/` | نمایش؛ ساخت فقط ادمین |
| GET/POST | `accounts/` | حساب‌های متعلق به کاربر |
| POST | `accounts/{id}/login-session/` | لینک کوتاه‌عمر noVNC |
| GET/POST | `tokens/` | توکن‌های scoped کاربر |
| GET/POST | `chats/` | گفتگوها و حافظه |
| POST | `assets/uploads/` | آپلود چندرسانه‌ای |
| POST | `jobs/` | ایجاد Job غیرهم‌زمان |
| GET | `jobs/{id}/` | وضعیت و پاسخ |
| POST | `jobs/{id}/cancel/` | لغو |
| GET | `jobs/{id}/events/` | SSE مجاز |
| GET | `artifacts/{id}/download/` | دانلود تحت مالکیت/امضای کوتاه‌مدت |
| GET | `admin/monitoring/` | مانیتورینگ با نقش ادمین |

## درخواست نمونه — متن
```bash
curl -X POST 'https://srun.ir/aiapimaker/api/v1/jobs/' \
  -H 'Authorization: Bearer YOUR_SCOPED_TOKEN' \
  -H 'Idempotency-Key: example-unique-id' \
  -H 'Content-Type: application/json' \
  -d '{
    "provider": "deepseek",
    "account_id": "ACCOUNT_UUID",
    "connector": "deepseek-harness",
    "prompt": "سلام، یک پاسخ کوتاه بده",
    "chat_id": null,
    "options": {"stream": false}
  }'
```

نمونه پاسخ برنامه‌ریزی‌شده (هنوز پیاده‌سازی نشده):
```json
{
  "job_id":"JOB_UUID",
  "status":"queued",
  "status_url":"/aiapimaker/api/v1/jobs/JOB_UUID/",
  "events_url":"/aiapimaker/api/v1/jobs/JOB_UUID/events/"
}
```

## ارسال فایل
فایل پیش از Job به `assets/uploads/` ارسال و `asset_id` برگردانده می‌شود. Job می‌تواند `asset_ids` دریافت کند. برای فایل‌های حجیم upload chunking در Stage 18 پیاده می‌شود؛ قابلیت دریافت صوت/ویدئو توسط مدل باید از Capability Matrix بررسی شود.

## پاسخ نتیجه
```json
{
  "job_id":"JOB_UUID",
  "status":"completed",
  "output":{"text":"پاسخ مدل","json":null},
  "artifacts":[{"id":"ARTIFACT_UUID","mime_type":"application/pdf","download_url":"https://srun.ir/aiapimaker/api/v1/artifacts/ARTIFACT_UUID/download/"}],
  "usage":{"status":"reported_or_estimated"}
}
```

## محدودیت‌های سخت
- توکن دارای scope فقط می‌تواند ProviderAccount متعلق به همان کاربر و مجازش را انتخاب کند.
- Job در صورت نبود اتصال مجاز با پاسخ خطای ساختاریافته `provider_unavailable` یا `authorization_required` برمی‌گردد؛ هیچ workaround برای ورود/کپچا/سهمیه وجود ندارد.
- هیچ API جدیدی به Flask قدیمی اضافه نمی‌شود؛ Django مالک API جدید است.
