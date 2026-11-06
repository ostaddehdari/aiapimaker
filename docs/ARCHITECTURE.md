# معماری مرجع AI API Maker

## هدف
`https://srun.ir/aiapimaker/` یک سرویس جدید چندکاربره است که **React فرانت‌اند مستقل** و **Django API مستقل** دارد و هیچ تغییری در سرویس فعلی `/aigetway/` در فاز نخست نمی‌دهد.

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
