import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faArrowTrendUp,
  faBolt,
  faCircleNodes,
  faCloudArrowUp,
  faGaugeHigh,
  faLayerGroup,
  faPlus,
  faRobot,
  faServer,
  faShieldHalved,
  faUsers,
} from '@fortawesome/free-solid-svg-icons';

function PageTitle({ eyebrow, title, subtitle }: { eyebrow: string; title: string; subtitle: string }) {
  return (
    <div className="page-heading">
      <span className="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </div>
  );
}

function MetricCard({ label, icon, detail }: { label: string; icon: typeof faRobot; detail: string }) {
  return (
    <article className="metric-card">
      <div className="metric-icon"><FontAwesomeIcon icon={icon} /></div>
      <span>{label}</span>
      <strong>—</strong>
      <small>{detail}</small>
    </article>
  );
}

const providerNames = [
  { name: 'ChatGPT / Codex', description: 'مدل‌های OpenAI و ابزارهای کدنویسی', initials: 'C' },
  { name: 'Gemini', description: 'مدل‌های هوش مصنوعی Google', initials: 'G' },
  { name: 'DeepSeek Harness', description: 'عامل خط فرمان DeepSeek', initials: 'D' },
  { name: 'Qwen', description: 'مدل‌ها و ابزارهای Qwen', initials: 'Q' },
  { name: 'Z.ai', description: 'مدل‌ها و ابزارهای Z.ai', initials: 'Z' },
  { name: 'Antigravity', description: 'اتصال آزمایشی در آینده', initials: 'A' },
];

export function AdminOverview() {
  return (
    <div className="page-stack">
      <PageTitle eyebrow="پنل مدیریت / نمای کلی" title="مرکز فرمان هوش مصنوعی"
        subtitle="از اینجا می‌توانید ارائه‌دهندگان، کاربران، پردازش‌ها و وضعیت منابع را مدیریت کنید." />
      <section className="metrics-grid" aria-label="آمار سامانه">
        <MetricCard label="ارائه‌دهندگان" icon={faLayerGroup} detail="پس از اتصال Django" />
        <MetricCard label="کاربران" icon={faUsers} detail="اطلاعات واقعی در Stage 08" />
        <MetricCard label="درخواست‌های در صف" icon={faBolt} detail="پس از راه‌اندازی Supervisor" />
        <MetricCard label="Worker فعال" icon={faServer} detail="پس از پایش زنده" />
      </section>
      <section className="dashboard-split">
        <article className="panel panel-large">
          <div className="panel-heading">
            <h2>نمایش کلی معماری</h2>
            <span className="section-chip">نقشه توسعه</span>
          </div>
          <div className="architecture-grid">
            <div><FontAwesomeIcon icon={faCloudArrowUp} /><strong>ورودی API</strong><small>Django REST</small></div>
            <div><FontAwesomeIcon icon={faCircleNodes} /><strong>Supervisor</strong><small>صف و مسیریابی</small></div>
            <div><FontAwesomeIcon icon={faRobot} /><strong>Connectorها</strong><small>حساب‌های ایزوله</small></div>
          </div>
          <p className="muted-text">در این مرحله هیچ درخواست واقعی به مدل‌ها ارسال نمی‌شود.</p>
        </article>
        <article className="panel panel-small">
          <div className="panel-heading"><h2>پایداری سیستم</h2><FontAwesomeIcon icon={faGaugeHigh} /></div>
          <div className="system-empty"><FontAwesomeIcon icon={faArrowTrendUp} /><strong>داده زنده در دسترس نیست</strong><small>شاخص‌های CPU، RAM و Jobها در Stage 34 متصل می‌شوند.</small></div>
        </article>
      </section>
    </div>
  );
}

export function AdminProviders() {
  return (
    <div className="page-stack">
      <PageTitle eyebrow="مدیریت / ارائه‌دهندگان" title="ارائه‌دهندگان هوش مصنوعی"
        subtitle="ثبت و تنظیم روش اتصال API، ابزار خط فرمان یا مرورگر مجاز برای هر ارائه‌دهنده." />
      <div className="page-toolbar">
        <span className="muted-text">فهرست زیر نمایشی است؛ هنوز به PostgreSQL متصل نشده است.</span>
        <button className="primary-button" type="button" disabled><FontAwesomeIcon icon={faPlus} /> افزودن ارائه‌دهنده</button>
      </div>
      <div className="provider-grid">
        {providerNames.map((provider) => (
          <article className="provider-card" key={provider.name}>
            <div className="provider-avatar">{provider.initials}</div>
            <div className="provider-copy"><h3>{provider.name}</h3><p>{provider.description}</p></div>
            <span className="section-chip">تنظیم‌نشده</span>
          </article>
        ))}
      </div>
    </div>
  );
}

export function AdminUsers() {
  return (
    <div className="page-stack">
      <PageTitle eyebrow="مدیریت / کاربران" title="مدیریت کاربران"
        subtitle="کاربران، نقش‌ها و سهمیه‌های API پس از اتصال سرویس هویت Django از این بخش مدیریت می‌شوند." />
      <div className="panel empty-panel">
        <FontAwesomeIcon icon={faUsers} />
        <h2>هنوز کاربری بارگذاری نشده است</h2>
        <p>در Stage 08 مدیریت کاربران و جداسازی داده‌ها به این صفحه متصل خواهد شد.</p>
        <button className="secondary-button" type="button" disabled><FontAwesomeIcon icon={faPlus} /> ایجاد کاربر</button>
      </div>
    </div>
  );
}

export function AdminSupervisor() {
  return (
    <div className="page-stack">
      <PageTitle eyebrow="مدیریت / زیرساخت" title="سوپروایزر و مانیتورینگ"
        subtitle="وضعیت صف، مرورگرها، تب‌ها، Workerها و مصرف منابع پس از اتصال بک‌اند نمایش داده می‌شود." />
      <section className="metrics-grid">
        <MetricCard label="پردازش هم‌زمان" icon={faBolt} detail="سقف قابل تنظیم" />
        <MetricCard label="مرورگرها و تب‌ها" icon={faRobot} detail="شروع درخواستی" />
        <MetricCard label="مصرف RAM" icon={faGaugeHigh} detail="پایش لحظه‌ای" />
        <MetricCard label="وضعیت امنیت" icon={faShieldHalved} detail="مجوزهای حساب" />
      </section>
      <div className="panel empty-panel">
        <FontAwesomeIcon icon={faServer} />
        <h2>اتصال به Worker هنوز فعال نشده است</h2>
        <p>هدف معماری، پذیرش درخواست‌های زیاد با تعداد محدود Worker و مرورگر است.</p>
      </div>
    </div>
  );
}
