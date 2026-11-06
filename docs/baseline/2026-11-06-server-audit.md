# Stage 01 — گزارش مبنا (ثبت از خروجی سرور)

**زمان نمونه:** 2026-11-06 18:08:20 UTC  
**منبع:** اجرای خواندنی `bash scripts/stage01_audit.sh` روی Ubuntu 24.04.5 LTS  
**وضعیت:** نیمه‌تمام — صرفاً گزارش، هیچ تغییر production انجام نشده است.

## مشاهدات تأییدشده
- `aigetway-api`، `aigetway-worker`، `nginx`، `postgresql` و `redis-server` همگی `active` هستند.
- نشانی Health سرویس قدیمی `/aigetway/healthz` مقدار `{"status":"ok","version":"0.6.0"}` داده است.
- تست نحو Nginx موفق بوده؛ هشدار `duplicate MIME type "text/html"` از `/etc/nginx/snippets/statichost-sitelinkmacker.conf:43` گزارش شده (هشدار غیرمانع).
- RAM: 11 GiB کل، 5.6 GiB استفاده‌شده، 6.0 GiB available؛ Swap: 4 GiB کل و **2.5 GiB مصرف‌شده**.
- دیسک root: 116 GiB کل، **102 GiB استفاده‌شده / 14 GiB آزاد / 89%**.
- ابزارها در PATH کاربر root: `python3`، Node.js مبتنی بر nvm، `npm`، `codex` و `dsh`.
- پورت‌های مرتبط فعلی `18765` و `18775` و پورت‌های `3081`/`3099` در localhost شنونده‌اند. **نباید برای AI API Maker رزرو شوند.**
- PostgreSQL روی `127.0.0.1:5432` موجود است؛ نصب PostgreSQL دوم پیش از بررسی لازم نیست.

## خطرها و تصمیم‌های موقت
1. **ریسک اصلی ظرفیت:** فضای 14 GiB برای نصب پشته جدید، تصویر مرورگر، cache و backup کافی فرض نشود. پیش از هر نصب/staging باید ظرفیت در Stage 01 بررسی و محل آزادسازی ایمن مشخص شود؛ چیزی خودکار حذف نشود.
2. **فشار حافظه:** 2.5 GiB Swap مصرف‌شده لزوماً نشانه Swap فعال جاری نیست. با `vmstat 1 3` نرخ `si/so` بررسی شود؛ اجرای مرورگرهای متعدد تا benchmark ممنوع.
3. **Nginx:** هشدار duplicate MIME به‌صورت Issue مجزا برای اصلاح آتی ثبت شود؛ اکنون reload یا ویرایش نیاز نیست.
4. **پایداری:** سرویس‌های Flask قدیمی، Codex، DeepSeek Harness و Antigravity دست‌نخورده بمانند.
5. **Credential:** هیچ فایل session، cookie، .env یا token در این گزارش یا repository ثبت نشده است.

## باقی‌مانده Stage 01
- W01.01: لیست سرویس‌های مرتبط و کانتینرها با نام‌های واقعی ناقص است.
- W01.02: نقشه دقیق Nginx بدون secret و اینکه `/aiapimaker/` آزاد است، تأیید شود.
- W01.03: **موفق:** Health و نسخه سرویس قبلی ثبت شد.
- W01.04: مسیر `codex` ثبت شد ولی نسخه، کاربر اجرایی و تست سلامت ناقص است.
- W01.05: مسیر `dsh` ثبت شد ولی نسخه کاربر سرویس و وضعیت نشست هنوز تأیید نشده است.
- W01.06: Antigravity نصب/عدم احراز هویت نیازمند بررسی محدود و مستند است.
- W01.07: **اولیه موفق:** CPU/RAM/Swap/Disk و پورت‌ها ثبت شد؛ روند Swap و حجم مسیرها نیاز به بررسی تکمیلی دارد.
- W01.08: این ثبت، پیش‌نویس risk register است؛ نهایی‌سازی پس از بررسی دیسک/پورت.

**وضعیت Gate:** `BLOCKED_FOR_INSTALL` تا زمانی که گزارش منابع و برنامه ظرفیت پذیرفته شود. این به معنی خرابی سرویس زنده نیست.

## گام بعد
اجرای صرفاً خواندنی `bash scripts/stage01_followup.sh` و بررسی خروجی بدون انتشار اطلاعات محرمانه. نتیجه در Issue #1 ثبت شود.


## پیوست: ممیزی تکمیلی 2026-11-06 18:24:41 UTC

**منبع:** خروجی کاربر از `nice -n 19 bash scripts/stage01_followup.sh`. خروجی اسکریپت به پایان رسیده، سپس اتصال SSH با `Connection reset by peer` قطع شده است. علت اتصال قطع‌شده از این داده‌ها معلوم نیست؛ هیچ نشانه‌ای از تغییر سیستم توسط اسکریپت وجود ندارد.

### فضای ذخیره‌سازی و ظرفیت
| مورد | اندازه |
|---|---:|
| Root filesystem | 116G کل / 102G استفاده‌شده / 14G آزاد / 89% |
| Inodes | فقط 17% مصرف‌شده؛ مشکل شمار inode نیست |
| /var/log | 3.9G |
| systemd journal (active+archived) | 3.7G از 3.9G لاگ؛ نامزد اول بازبینی سیاست retention |
| /var/backups | 167M |
| /var/cache | 177M |
| /var/lib/docker | 3.6G؛ **بدون پاکسازی عمومی/prune** |
| /var/lib/postgresql | 4.5G؛ **هرگز حذف دستی نشود** |
| /var/lib/aigetway | 1.3G؛ **فایل‌های نشست/داده حذف نشود** |
| /root/.npm | 844M؛ بعد از بررسی cache و نیاز نسخه‌ها تصمیم‌گیری شود |
| /root/.cache | 94M |
| /opt | 15G؛ اندازه زیرپوشه‌ها فقط خواندنی بررسی شود |

### فشار CPU/Swap
- Swap استفاده‌شده حدود 2.63GiB در زمان اندازه‌گیری (آرایه `swpd=2756804 KiB`).
- نمونه‌های متوالی `vmstat` نرخ `si=0` و `so=0` داشته‌اند؛ **Swap پرشده به معنی thrashing در آن لحظه نیست**.
- نمونه‌های فعلی درصد `st` برابر **27% و 29%**، و `id` برابر 20–22% دارند. `steal` بالا می‌تواند نشان‌دهنده رقابت منابع میزبان مجازی باشد؛ باید تکرار و در صورت استمرار با ارائه‌دهنده VPS پیگیری شود.
- میانگین بار و `r=13–14` نشان‌دهنده صف اجرای CPU؛ از استقرار Browser Worker موازی تا سنجش ظرفیت پرهیز شود.

### وضعیت ابزارها
- `codex-cli 0.154.0`
- `dsh 0.2.1-rc.5`
- Service unitهای `aigetway-api` و `aigetway-worker` و `antigravity-gateway-api` و `antigravity-gateway-worker` پیدا شده‌اند. **وضعیت ورود Antigravity هنوز ثابت نشده است**.
- Nginx فقط `location = /aigetway` و `location ^~ /aigetway/` در grep گزارش کرده است؛ **نصب /aiapimaker هنوز انجام نشده**.

### کارهای بعدی / منع تغییر خودسر
1. اگر تأیید عملیاتی شد، نگهداری journal را با `journalctl --rotate` و `journalctl --vacuum-size=1G` محدود کنید؛ این کار **لاگ‌های قدیمی را حذف می‌کند**، بنابراین پیش از اجرا نیاز به سیاست retention و احتیاط در زمان حادثه دارد.
2. بدون پاک‌سازی، `du -xhd1 /opt` و مسیرهای بزرگ را با `nice`/`ionice` بررسی کنید.
3. صحت اتصال SSH، `systemctl is-active` و `curl .../healthz` بعد از reset بررسی شود.
4. پیش از Stages نصب، فضای پایدار و فشار CPU به حد قابل‌قبول برسد.
5. هیچ `docker system prune`، `rm -rf /var/lib/postgresql`، `swapoff` یا حذف نشست انجام نشود.

**Gate:** `STAGE_01_IN_PROGRESS / CAPACITY_REVIEW_REQUIRED`؛ هنوز مجوز شروع نصب Stage 02 داده نشده است.

## پیوست: پاک‌سازی تأییدشده Journal و سلامت سرور

**منبع:** خروجی ارسال‌شده پس از اجرای دستی `journalctl --rotate` و `journalctl --vacuum-size=1G`.

- با دستور vacuum، حدود **2.7G** از archived journal آزاد شد.
- فضای journal پس از عملیات **980.1M** گزارش شد.
- root filesystem پس از آن **99G استفاده، 17G آزاد، 86%** گزارش شد.
- `aigetway-api`، `aigetway-worker`، `nginx`، `postgresql` و `redis-server` همچنان **active** بودند.
- `https://srun.ir/aigetway/healthz` پاسخ `{"status":"ok","version":"0.6.0"}` داده است.
- در `/opt` مسیرهای بزرگ شامل `/opt/teltest` (3.6G)، `/opt/tamap` (2.2G)، `/opt/teamgram-compat-test` (1.7G)، `/opt/stagepilot` (1.3G) و `/opt/vianoor-opensearch-runtime` (1.3G) هستند؛ **هیچ‌کدام بدون ممیزی یا درخواست صریح حذف نشوند**.
- نام و نشانی `srun.ir/aiapimaker` موقتی است و پیش از استقرار باید URL جدید تعیین شود. مبنای معماری در [ARCHITECTURE.md](../../ARCHITECTURE.md) اصلاح شده است.

**وضعیت:** بخشی از ریسک دیسک رفع شد؛ پایش ظرفیت CPU و انتخاب مقصد دامنه همچنان باز است. Stage 01 هنوز کامل نیست.


## پیوست: بررسی قطع SSH و تأیید دوباره سلامت — 2026-11-06 18:54 UTC

**منبع:** خروجی جدید کاربر از اتصال Git Bash به SSH سرور.

- اتصال SSH قبلی با `Connection reset by peer` قطع شد، اما ورود مجدد با `ssh -t -p 2233 root@5.61.27.185` موفق بود؛ علت قطع ارتباط از این خروجی قابل تشخیص نیست.
- MOTD جدید: Load `7.78`، دیسک `85.9%`، RAM `62%` و Swap `68%`. این مقادیر snapshot هستند، نه اثبات OOM یا خرابی.
- پس از reconnect، `aigetway-api`، `aigetway-worker`، `nginx`، `postgresql` و `redis-server` همگی `active` گزارش شدند.
- Health سرویس قدیمی: `{"status":"ok","version":"0.6.0"}`. لذا پس از قطع SSH دست‌کم در زمان تست، این سرویس سالم بوده است.
- خطای `nvm` از تنظیم `prefix` در `/root/.npmrc` گزارش می‌شود. این پیام مانع ورود SSH نیست؛ در Stage مستقل و بدون تغییر محیط Node سرویس‌ها بررسی شود.
- دامنه `srun.ir/aiapimaker` همچنان موقت است؛ مقصد جدید هنوز مشخص نشده. تغییر Nginx یا DNS انجام نشده است.

### بررسی امن پیشنهادی
- `vmstat 1 5` و `free -h` برای بررسی si/so فعلی و Available RAM.
- `systemctl is-active ssh` و `journalctl -u ssh --since "-2 hours" --no-pager` با بررسی دستی و حذف IP/شناسه‌های حساس پیش از اشتراک.
- `journalctl -k --since "-2 hours" --no-pager | grep -Ei 'out of memory|oom|killed process'` برای تشخیص قطع فرایندها؛ نبود خروجی = فقط نبود رخداد در بازه بررسی.
- اجرای ممیزی بدون نصب سرویس جدید یا حذف داده.
