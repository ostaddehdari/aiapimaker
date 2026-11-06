# معماری مرجع AI API Maker

## هدف
نشانی فعلیِ **موقت و قابل تغییر** `https://srun.ir/aiapimaker/` برای یک سرویس جدید چندکاربره است که **React فرانت‌اند مستقل** و **Django API مستقل** دارد و هیچ تغییری در سرویس فعلی `/aigetway/` در فاز نخست نمی‌دهد.

## مرزهای سرویس
```text
Browser -> Nginx /aiapimaker/ -> React SPA (static)
        -> Nginx /aiapimaker/api/v1/ -> Django ASGI/DRF
                                          |-> PostgreSQL (source of truth)
                                          |-> Redis/Celery (queue + realtime)
                                          |-> private Artifacts store
                                          |-> Supervisor -> Account-scoped Worker
                                                               |-> Codex CLI adapter
                                                               |-> DeepSeek Harness adapter
                                                               |-> Antigravity adapter (awaiting auth)
                                                               |-> Claude Code/Codex Cloud stubs
                                                               |-> Official provider APIs
                                                               |-> Permitted browser adapter
Legacy: /aigetway/ -> existing Flask services (unchanged)
```

## فناوری قطعی
- Frontend: React, Vite, TypeScript, TanStack Query, React Router, GSAP, Vazirmatn/Vazir، Font Awesome.
- Backend: Django, DRF, PostgreSQL, OpenAPI, ASGI + Channels یا SSE.
- Queue: Redis + Celery; PostgreSQL منبع وضعیت پایدار Job است؛ Redis تنها منبع حقیقت نیست.
- Browser: Playwright + Chromium + Xvfb/noVNC برای ورود دستی و اتصال مجاز؛ session profile با مالک مستقل و قفل تک‌اجرایی.
- Runtime: systemd مستقل و user بدون root، Nginx زیرمسیر، شبکه داخلی و TLS موجود.

## تفکیک مدل‌ها
- `Provider`: شرکت/سرویس (ChatGPT, Gemini, DeepSeek, Qwen, Z.ai).
- `Connector`: پیاده‌سازی فنّی و نسخه‌دار (CLI/Official API/Browser-authorized).
- `ProviderAccount`: اتصال حساب مشخص متعلق به کاربر.
- `ModelCapability`: نوع ورودی/خروجی واقعی هر connector.
- `ApiToken`: مجوز به Provider/Account/عملیات که قابل‌لغو است.
- `Job`: درخواست پایدار در صف با tenant، مالک، account و idempotency.
- `Chat/Message`: تاریخچه خود کاربر؛ context تنها با مجوز منتقل شود.
- `Artifact`: فایل خصوصی با download URL مالک‌محور و expiration.

## معیارهای امنیت
- حساب A به پروفایل B و کلیدهای B دسترسی ندارد؛ ACL در همه QuerySetها و سرویس ذخیره‌سازی اعمال شود.
- noVNC تنها از طریق short-lived ticket و احراز هویت Django، نه پورت VNC عمومی.
- کلیدها و browser cookies در repository، log، API response یا UI عمومی منتشر نمی‌شوند.
- CLIهای کدنویسی با کاربر محدود و workspace sandbox اجرا شوند، نه root.
- قابلیت subscription login مخصوص استفاده مجاز از CLI است و جایگزین OpenAI API نیست.
- اجرای automation روی چت وب اشخاص ثالث منوط به مجوز همان ارائه‌دهنده است؛ در غیر این صورت از official API استفاده یا آن Provider غیرفعال می‌شود.

## ظرفیت مبنا
- گزارش قبلی سرور: 11 GiB RAM، 4 GiB swap با مصرف قابل‌توجه، 25 GiB فضای دیسک در زمان ثبت؛ **این اعداد باید در Stage 01 تازه‌سازی شوند**.
- پذیرش هم‌زمان ۱۰۰ درخواست به معنای ۱۰۰ browser نیست. برای MVP حداکثر یک browser job فعال، صف پایدار و بارگذاری درخواستی تعیین شده و پس از benchmark تغییر می‌کند.
- انقضای نشست یا CAPTCHA = توقف و اعلان کاربر، نه تلاش برای bypass.

## پایداری و مهاجرت
- Release جدید در systemd و PostgreSQL جدا ساخته می‌شود.
- نام‌های پورت داخلی و مسیرهای داده تا ممیزی Stage 01 قطعی نیستند.
- Nginx فقط بعد از `nginx -t` و Backup تغییر می‌کند.
- برای اجرای واقعی هر Connector، آزمون end-to-end و feature flag الزامی است.
- بازنشستگی Flask قبلی خارج از Scope است مگر پس از انتقال و قبول صریح.

## تصمیم جدید: دامنه و مسیر عمومی قابل تغییر (2026-11-06)

**درخواست مالک پروژه:** نام/نشانی نهایی سایت قرار است تغییر کند. تا اعلام آدرس جدید، نام `srun.ir/aiapimaker` صرفاً `TEMPORARY_PUBLIC_URL` و مقصد استقرار **غیرقطعی** است. نام repository `aiapimaker` و شناسه‌های داخلی به domain وابسته نیستند.

### تنظیمات لازم در Django/React/Nginx

| تنظیم | هدف |
|---|---|
| `APP_PUBLIC_ORIGIN` | ریشه HTTPS نهایی؛ مثال فعلی `https://srun.ir` |
| `APP_BASE_PATH` | مسیر React؛ مثال موقت `/aiapimaker/` یا `/` در دامنه مستقل |
| `API_BASE_PATH` | مسیر API زیر مسیر اپ؛ مثال `/aiapimaker/api/v1/` |
| `VITE_BASE_PATH` | `base` برای build فایل‌های React و Router basename |
| `DJANGO_ALLOWED_HOSTS` | میزبان‌های مجاز شامل آدرس نهایی پس از تأیید |
| `CSRF_TRUSTED_ORIGINS` | originهای مجاز دقیق؛ بدون wildcard عمومی |
| `CORS_ALLOWED_ORIGINS` | فقط در صورت جداشدن origin رابط و API |
| `MEDIA_PUBLIC_BASE_URL` | صدور لینک فایل روی دامنه جدید یا از reverse proxy |
| `OAUTH_REDIRECT_BASE_URL` | مسیرهای redirect ثبت‌شده برای احراز هویت‌های مجاز |

- backend و frontend باید URLها را از configuration تولید کنند؛ هیچ URL مربوط به دامنه موقت در business logic و API payload ثابت نباشد.
- تا تعیین نام نهایی، تنظیم Nginx، گواهی TLS، redirect یا DNS در Production تغییر نکند.
- پس از اعلام دامنه، کنترل DNS، TLS، دامنه مجاز Django، تنظیم cookie، CSRF و callbackهای OAuth و تست subpath/root انجام شود.
- امکان redirect موقت/دائمی از نشانی سابق **فقط پس از راه‌اندازی موفق مقصد جدید و تصمیم مالک** فعال شود.
