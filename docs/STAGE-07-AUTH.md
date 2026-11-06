# Stage 07 — قرارداد ورود، نشست و بازیابی امن Django

**وضعیت:** این APIها در شاخه آزمایشی Django ساخته می‌شوند. **ورود واقعی React** تا Stage 09 و **استقرار عمومی** تا Gate امنیتی انجام نمی‌شود. مسیر عمومی و دامنه هنوز انتخاب نشده است.

## ۸ کار این مرحله

| Work | خروجی |
|---|---|
| W07.01 | کاربر UUID با username/email و Django password hasher از Stage 06؛ بدون ذخیره رمز خام |
| W07.02 | `csrf/login/logout/me/change-password/password-reset` در DRF و حسابرسی |
| W07.03 | session cookie `HttpOnly`/`SameSite=Lax`؛ `Secure` فقط در HTTPS staging/production؛ همه POSTهای حساس محافظت‌شده با CSRF |
| W07.04 | تاریخ انقضای نشست و فهرست دستگاه‌های شخصی، revoke و اجرای middleware برای قطع نشست مسدودشده |
| W07.05 | طراحی MFA اختیاری برای مرحله امنیت: TOTP/WebAuthn (فعلاً هیچ ادعایی درباره فعال‌بودن MFA نشود) |
| W07.06 | throttle پایدار دیتابیس بر شناسه کاربری و REMOTE_ADDR هش‌شده با HMAC، audit بدون ذخیره IP/رمز |
| W07.07 | آزمون CSRF، brute-force، password change/reset، revoke، انقضا و جداسازی دستگاه‌ها |
| W07.08 | schema OpenAPI و نمونه‌های curl در سند حاضر |

## نمونه قرارداد REST

Prefix نمونه: `/aiapimaker/api/v1/auth/`. در Production این مسیر با `API_BASE_PATH` متناسب با دامنه نهایی ساخته می‌شود.

| Method | Path | توضیح |
|---|---|---|
| GET | `csrf/` | صدور cookie و token از طریق JSON برای هدر درخواست‌های بعدی |
| POST | `login/` | username/password، برگرداندن user و session id در قالب UUID؛ کلید نشست فقط Cookie است |
| GET | `me/` | اطلاعات کاربر، نقش admin فقط با شرط staff/superuser |
| POST | `logout/` | باطل‌کردن نشست جاری |
| GET | `sessions/` | فقط نشست‌های همان کاربر |
| POST | `sessions/revoke/` | باطل‌کردن نشست متعلق به همان حساب |
| POST | `change-password/` | تغییر رمز با رمز قبلی، لغو دستگاه‌های دیگر |
| POST | `password-reset/request/` | پاسخ مشترک بدون آشکارسازی وجود حساب؛ فقط در صورت فعال‌سازی SMTP |
| POST | `password-reset/confirm/` | token یک‌بارمصرف Django، اعتبارسنجی رمز، لغو همه نشست‌ها |

### نمونه curl برای مسیر localhost و حساب تست

در این مثال سرویس Django باید **به‌شکل جداگانه و تنها در محیط آزمون** در دسترس باشد. این دستورها از نظر قراردادی هستند؛ در `srun.ir` هنوز اجرا نمی‌شوند:

```bash
BASE="http://127.0.0.1:19361/aiapimaker/api/v1/auth"
curl -sS -c cookies.txt "$BASE/csrf/" -o csrf.json
# مقدار csrf_token را از csrf.json بخوانید؛ آن را در خروجی عمومی یا GitHub ارسال نکنید.
CSRF_TOKEN="VALUE_FROM_CSRF_JSON"
curl -sS -b cookies.txt -c cookies.txt \
  -H "Content-Type: application/json" -H "X-CSRFToken: $CSRF_TOKEN" \
  -d '{"username":"demo","password":"YOUR_TEST_PASSWORD"}' \
  "$BASE/login/" -o login.json
# مقدار csrf_token جدید را از login.json بگیرید؛ Django پس از ورود آن را می‌چرخاند.
LOGIN_CSRF_TOKEN="UPDATED_TOKEN_FROM_LOGIN_JSON"
curl -sS -b cookies.txt "$BASE/me/"
curl -sS -b cookies.txt -H "X-CSRFToken: $CSRF_TOKEN" \
  -X POST -H "Content-Type: application/json" -d '{}' "$BASE/logout/"
```

**هشدار:** فایل Cookie موقت را خارج از Git نگه دارید و بعد از آزمون حذف کنید. HTTPS و تنظیم Secure Cookies در محیط واقعی الزامی است. برای اپ SPA می‌توان Token را از JSON خواند، چون CSRF cookie در این پروژه HttpOnly است.

## سیاست امنیت و بازه‌های زمانی
- Session TTL پیش‌فرض ۱۲ ساعت است و با ورود مجدد، تغییر رمز یا لغو نشست کنترل می‌شود.
- پس از ۵ تلاش ناموفق یک کاربر در ۱۵ دقیقه یا ۲۵ خطا از یک IP، درخواست موقتاً قفل می‌شود. IP و شناسه در DB به‌صورت HMAC ذخیره می‌شوند.
- برای پراکسی Nginx، اگر `REMOTE_ADDR` همه کاربران یکسان باشد، قفل سراسری IP می‌تواند اشتباه رخ دهد. تنظیم **trusted real-IP** فقط با شبکه‌های معتمد و بازنویسی هدرها در مرحله Nginx بررسی شود. به هدر `X-Forwarded-For` خام اعتماد نکنید.
- درخواست بازیابی رمز در staging/production تا هنگام تنظیم و آزمون SMTP معتبر **غیرفعال** می‌ماند. متن پاسخ نباید وجود کاربر را آشکار کند.
- `AuthDeviceSession` تنها هش شناسه نشست Django را ذخیره می‌کند؛ نه کوکی قابل‌استفاده مجدد.
- با `AuthEvent` فقط event، شناسه هش‌شده، وضعیت موفقیت و شناسه داخلی کاربر ثبت می‌شود.
- در این مرحله هنوز **MFA فعال نشده است**. طرح پیشنهادی: ادمین‌ها TOTP با کد بازیابی هش‌شده و مدیران حساس WebAuthn/passkey را در Stage امنیت با ویژگی اختیاری فعال کنند. تا آن زمان هیچ ادعای MFA-enforced برای Admin نداشته باشیم.
- پلتفرم اصلی نباید اطلاعات نشست ارائه‌دهندگان AI را با نشست ورود کاربران مخلوط کند؛ Provider OAuth و ChatGPT/DeepSeek account login ماژول دیگری است.

## معیار قبولی

Django `check`، Migrationهای جدید `users`، آزمون‌های ورود، CSRF، قفل موقت، لغو نشست، بازیابی رمز و Postgres CI سبز شوند؛ OpenAPI مسیرهای auth را فهرست کند. این نتیجه **تنها برای محیط CI** پذیرفته می‌شود و مجوز استقرار عمومی محسوب نمی‌شود.

## فعال‌سازی بازیابی رمز در staging/production

`PASSWORD_RESET_ENABLED=false` پیش‌فرض است. برای فعال‌سازی، SMTP واقعی را در EnvironmentFile محرمانه خارج از Git تنظیم کنید: `EMAIL_HOST`، `EMAIL_PORT`، `EMAIL_HOST_USER`، `EMAIL_HOST_PASSWORD` و `DEFAULT_FROM_EMAIL`. بدون این تنظیمات Django باید از فعال‌شدن بازیابی رمز خودداری کند. مقدارهای واقعی در GitHub، لاگ یا Swagger قرار نگیرند. در حالت CI فقط `locmem.EmailBackend` استفاده می‌شود.

در خروجی ورود Django، `csrf_token` جدید برگردانده می‌شود؛ در Frontend لازم است پس از هر login موفق این مقدار جایگزین مقدار قبلی شود. برای درخواست‌های تغییردهنده داده، Cookie Session به‌تنهایی کافی نیست و هدر `X-CSRFToken` نیز الزامی است.
