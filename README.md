# aw-mcp

سرور MCP با پایتون برای پرسیدن سؤال‌های تحلیلی از انبار داده‌ی `AdventureWorksDW_Custom` (SQL Server) از داخل Claude Desktop.

بدون نوشتن SQL، از Claude بپرسید «رشد سالانه‌ی فروش هر دسته چقدر بوده؟» و Claude با ابزارهای این سرور مستقیم از انبار داده جواب می‌گیرد.

## ابزارها

| ابزار | کار | پارامترها |
|---|---|---|
| `describe_model` | فهرست جدول‌ها با تعداد ردیف و ستون‌ها | ندارد |
| `sales_summary` | فروش، تعداد و تعداد سفارش | `group_by` (year, quarter, month, category, territory)، `year`، `channel` |
| `top_products` | پرفروش‌ترین محصولات | `limit`، `year`، `channel`، `by` (sales, units) |
| `yoy_growth` | رشد سالانه نسبت به سال قبل | `group_by` (total, category, territory)، `metric` (sales, units)، `channel` |
| `kpi_summary` | فروش، سفارش، میانگین ارزش سفارش، سود و حاشیه‌ی سود تخمینی | `year`، `channel` |

مقدار `channel` یکی از `internet`، `reseller` یا `all` است.

## نمونه‌ی سؤال

- «ساختار مدل داده را توضیح بده.»
- «فروش فصلی سال ۲۰۲۴ را نشان بده.»
- «۱۰ محصول پرفروش کانال اینترنتی را بگو.»
- «از ابزار yoy_growth با group_by=category استفاده کن و رشد سالانه‌ی هر دسته را نشان بده.»
- «KPIهای سال ۲۰۲۴ را بده.»

## پیش‌نیازها

- Python نسخه‌ی ۳٫۱۰ یا بالاتر
- SQL Server با دیتابیس `AdventureWorksDW_Custom`
- ODBC Driver 17 یا 18 for SQL Server
- Claude Desktop

## نصب

```powershell
git clone https://github.com/ghaani/aw-mcp.git
cd aw-mcp
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

## تنظیمات

فایل `.env` را باز کنید و مقدارها را با سیستم خودتان عوض کنید:

```
DB_SERVER=localhost
DB_NAME=AdventureWorksDW_Custom
DB_DRIVER=ODBC Driver 18 for SQL Server
DB_TRUSTED_CONNECTION=yes
DB_TRUST_CERT=yes
```

- با Windows Authentication همین مقدارها کافی است.
- برای SQL Login مقدار `DB_TRUSTED_CONNECTION=no` بگذارید و `DB_USER` و `DB_PASSWORD` را اضافه کنید.
- فایل `.env` در گیت قرار نمی‌گیرد.

## اتصال به Claude Desktop

بخش `mcpServers` فایل تنظیمات Claude Desktop را مطابق [docs/claude_desktop_config.example.json](docs/claude_desktop_config.example.json) کامل کنید و مسیر `python.exe` داخل `.venv` را جایگزین `C:/path/to/aw-mcp` کنید.

بعد Claude Desktop را کامل ببندید (آیکون کنار ساعت ← Quit) و دوباره باز کنید. در یک چت **جدید**، نام ابزار را صریح بگویید تا Claude حدس نزند.

> نکته‌ی ویندوز: اگر Claude Desktop به‌صورت MSIX نصب شده باشد، فایل تنظیمات واقعی ممکن است در `%LOCALAPPDATA%\Claude-Data\...` باشد و نه `%APPDATA%\Claude`.

## تست‌ها

```powershell
python -m pytest -v
```

تست‌های محاسباتی و اعتبارسنجی ورودی به دیتابیس نیاز ندارند. تست‌های یکپارچگی فقط وقتی اجرا می‌شوند که SQL Server در دسترس باشد و در غیر این صورت خودکار `skipped` می‌شوند.

## ساختار پروژه

```
aw-mcp/
├── src/aw_mcp/
│   ├── server.py            # ثبت ابزارها و اجرای سرور (stdio)
│   ├── db.py                # اتصال و اجرای کوئری فقط‌خواندنی
│   ├── logging_config.py    # لاگ در فایل و stderr
│   └── tools/
│       ├── common.py        # توابع مشترک
│       ├── model.py         # describe_model
│       ├── sales.py         # sales_summary, top_products
│       ├── yoy.py           # yoy_growth
│       └── kpi.py           # kpi_summary
├── tests/
├── docs/
└── pyproject.toml
```

## امنیت و محدودیت‌ها

- فقط کوئری‌های `SELECT` و `WITH` اجرا می‌شوند. این یک سد ایمنی ساده است و جایگزین محدود کردن دسترسی نیست؛ برای اتصال از یک حساب **فقط‌خواندنی** (مثلاً `db_datareader`) استفاده کنید.
- ابزارها فقط SQL ثابت و پارامتری اجرا می‌کنند و ورودی کاربر مستقیم داخل SQL نمی‌رود. مقدارهای `group_by` و `channel` از فهرست مجاز انتخاب می‌شوند.
- لاگ‌ها در `logs/aw_mcp.log` و stderr نوشته می‌شوند. خروجی استاندارد (stdout) برای پروتکل MCP رزرو است.

## نکته‌های داده

- در این دیتابیس سال ۲۰۲۲ فقط ۸ ماه و سال ۲۰۲۵ فقط ۶ ماه داده دارد. ابزار `yoy_growth` برای هر ردیف فیلد `comparable` برمی‌گرداند که فقط وقتی `true` است که هر دو سال کامل (۱۲ ماه) باشند.
- مقدار `gross_profit_est` یک **تخمین** است (فروش منهای تعداد ضرب در هزینه‌ی استاندارد محصول).

## مسیر توسعه

- اتصال به مدل SSAS Tabular و اجرای کوئری DAX
- فرهنگ داده (توضیح جدول‌ها و ستون‌ها) برای `describe_model`
- ابزارهای تحلیل مشتری و منطقه
