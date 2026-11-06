# Stage 01 — ممیزی و baseline امن

**هدف:** جمع‌آوری شواهد از سرور Ubuntu موجود، بدون هیچ نصب، restart، reload، ویرایش Nginx یا استفاده از secret.

**هدف استقرار:** `https://srun.ir/aiapimaker/` (هنوز ساخته نشده)  
**بستر قبلی:** `srun.ir/aigetway/` نسخه گزارش‌شده 0.6.0، Codex، DeepSeek Harness، Antigravity بدون حساب تأییدشده.

## هشت Work و خروجی موردنیاز
- [ ] W01.01 — لیست خواندنی سرویس‌های systemd و کانتینرهای AI Gateway؛ فایل `baseline/services.txt`
- [ ] W01.02 — موقعیت include و locationهای Nginx مرتبط بدون نمایش secret؛ فایل `baseline/nginx-map.md`
- [ ] W01.03 — ثبت health و نسخه Gateway سابق بدون افشای credential؛ فایل `baseline/health.json`
- [ ] W01.04 — تشخیص Codex version، مسیر binary و Linux user با رعایت عدم نمایش Auth؛ فایل `baseline/codex.md`
- [ ] W01.05 — تشخیص DeepSeek Harness version و وضعیت ورود بدون کپی کوکی؛ فایل `baseline/deepseek.md`
- [ ] W01.06 — بررسی نصب Antigravity، بدون Login اجباری یا اجرای دستور نامطمئن؛ فایل `baseline/antigravity.md`
- [ ] W01.07 — snapshot منابع CPU/RAM/Swap/Disk و پورت‌های LISTEN؛ فایل `baseline/resources.md`
- [ ] W01.08 — گزارش خطرها، نقاط حفظ سرویس و طرح بازگشت `baseline/risk-register.md`

## اجرای کاملاً خواندنی
از Git clone شده پروژه و پس از بررسی اسکریپت:

```bash
git clone https://github.com/ostaddehdari/aiapimaker.git
cd aiapimaker
sed -n '1,240p' scripts/stage01_audit.sh
bash scripts/stage01_audit.sh
```

اسکریپت هیچ فایل، سرویس یا بسته‌ای روی میزبان تغییر نمی‌دهد و خروجی را فقط در ترمینال چاپ می‌کند. **خروجی خام را قبل از اشتراک بازبینی کن**؛ نباید توکن، ایمیل خصوصی یا secret در آن باشد.

## دستورات مستقل بازبینی
```bash
systemctl is-active aigetway-api aigetway-worker
curl -fsS --max-time 8 https://srun.ir/aigetway/healthz
nginx -t
free -h
df -h /
ss -lnt
```

این‌ها جایگزین راه‌اندازی Stage 01 هستند و هیچ Login جدید یا تغییر تولیدی انجام نمی‌دهند.

## خروجی‌های قابل پذیرش
1. سند سرویس‌های فعال/غیرفعال با زمان بررسی؛
2. فهرست مسیرهای Nginx و شناسه‌های پورت بدون انتشار config محرمانه؛
3. اعتبارسنجی Codex/DSH/Antigravity بدون حذف/تعویض نشست‌ها؛
4. شناسایی محیط staging و محدودیت منابع با ارقام تازه؛
5. رأی `READY_FOR_STAGE_02` یا `BLOCKED` با دلیل.

**DoD:** دقیقاً ۸ Work بسته شود، هیچ سرویس عملیاتی تغییر نکند و شواهد در PR ثبت شوند.
