# Stage 03 — نقشه Staging مستقل و استقرار امن

**وضعیت:** طراحی و dry-run؛ هیچ نصب یا استقرار production در این Stage مجاز نیست.  
**وابستگی:** Stage 02 و تکمیل Gate عملیاتی Stage 01.  
**دامنه نهایی:** در انتظار تعیین مالک. از `srun.ir/aiapimaker` فقط به‌عنوان نشانی **موقت** یاد شود.

## هشت قرارداد و شواهد

| Work | قرارداد |
|---|---|
| W03.01 | محیط staging ابتدا فقط در `127.0.0.1` و بدون Nginx عمومی کار کند. React و Django مستقل‌اند. |
| W03.02 | کاربران سرویس `aiapimaker-web` و `aiapimaker-worker` (اسامی پیشنهادی)، واحدهای `aiapimaker-api.service` و `aiapimaker-worker.service` مجزا؛ پورت‌های **پیشنهادی** 19361 و 19362 فقط پس از راستی‌آزمایی اشغال نبودن قطعی شوند. |
| W03.03 | `.env.example` فاقد رمز و `infra/staging.env.example` برای الگوی local-only ایجاد شود؛ هر secret واقعی فقط خارج repo. |
| W03.04 | PostgreSQL قبلی shared server فقط با DB/role اختصاصی، بدون دستکاری دیتابیس قدیمی. Redis DB/namespace اختصاصی (یا instance مجزا پس از benchmark). فایل‌ها: `/var/lib/aiapimaker/{artifacts,uploads,sessions}` با owner جدا و permission 0700؛ مسیر فقط پیشنهاد است، پوشه هنوز ساخته نشده. |
| W03.05 | اجرای systemd با user بدون root، cgroup limits، `NoNewPrivileges`، قفل account profile و سقف اولیه **یک Job مرورگری فعال**؛ سرویس‌های Flask/Antigravity دست نخورند. |
| W03.06 | Snapshot دیتابیس، آرشیو artifactها، حفظ فایل پیکربندی امن و release pointer قبل از هر تغییر؛ طرح rollback فقط پس از backup restore test. |
| W03.07 | شرایط Python >=3.11، Node >=22، PostgreSQL >=14، Nginx و Redis در preflight **بررسی** شوند؛ انتخاب نسخه محصول و مهاجرت دیتابیس به Stage 04/06 موکول شود. |
| W03.08 | `bash scripts/stage03_preflight.sh` فقط read-only است؛ `CHECK_PASS` و `CHECK_WARN` و `CHECK_BLOCKED` را جدا گزارش کند؛ هیچ config، Nginx یا داده‌ای را تغییر نمی‌دهد. |

## مرزهای شبکه و مسیر
```text
Internet ──> Nginx موجود (بدون تغییر تا تأیید مرحله 39)
              ├─ /aigetway/ ---> Flask قدیمی :18765 (دست نزن)
              └─ (آینده) public origin config ---> React static
                                            └---> Django ASGI localhost:19361

Staging NOW: 127.0.0.1:19361 API و 127.0.0.1:19362 frontend preview
PORTS ARE PROPOSED — do not bind if occupied; no public exposure.
```

## مقادیر محیطی وابسته به دامنه
`APP_PUBLIC_ORIGIN`، `APP_BASE_PATH`، `API_BASE_PATH`، `VITE_BASE_PATH`، `DJANGO_ALLOWED_HOSTS`، `CSRF_TRUSTED_ORIGINS`، `CORS_ALLOWED_ORIGINS` (فقط در صورت نیاز)، `OAUTH_REDIRECT_BASE_URL` و `MEDIA_PUBLIC_BASE_URL` باید از محیط خوانده شوند؛ نه از کد hardcode.

## مرزهای منابع
در بررسی 2026-11-06 سرور 11GiB RAM و 4GiB swap داشت، 17GiB دیسک آزاد و CPU steal لحظه‌ای تا 23% بود. این‌ها baseline موقت هستند، نه تضمین ظرفیت. تا زمان مانیتورینگ، Workerهای پرمصرف و Chromiumهای موازی فعال نشوند. برای استقرار production، سیاست محافظه‌کارانه **حداقل 20GiB دیسک آزاد** پیشنهاد می‌شود (پس وضعیت قبلی نیازمند بررسی/افزایش ظرفیت است). آستانه staging خشک، هشدار کمتر از 20GiB و مانع کمتر از 10GiB است.

## پشتیبان‌گیری و بازگشت (طرح، نه اجرا)
1. قبل از تغییرات واقعی، بکاپ آزمایش‌شده DB اختصاصی و media با checksum گرفته شود.
2. مسیر release با pointer/ symlink اتمیک و سرویس مستقل باشد.
3. هنگام rollback، صف drain و migration compatibility بررسی شود.
4. release پیشین re-point، سلامت endpoints و رجوع به DB state با روش مستند تأیید شود.
5. در هیچ مرحله rollback، دیتابیس `aigetway` یا نشست‌های `dsh`/Codex/Antigravity حذف یا جایگزین نشوند.

## دستورات فقط-خواندنی
```bash
cd /root/aiapimaker-stage03
bash -n scripts/stage03_preflight.sh
bash scripts/stage03_preflight.sh
```

خروجی فوق صرفاً ارزیابی آمادگی است و مجوز تغییر production نیست.

## Definition of Done
هشت Work در اسناد/الگوها قابل ردیابی باشند، وضعیت پورت و منابع از سرور واقعی تایید شود و CI سبز باشد. پایان Stage 03 به معنی نصب Django/React نیست.
