import { useState } from 'react';
import type { FormEvent } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faArrowUp,
  faCircleNodes,
  faCloudArrowUp,
  faKey,
  faPaperclip,
  faPlus,
  faRobot,
  faShieldHalved,
  faWandMagicSparkles,
} from '@fortawesome/free-solid-svg-icons';

type DemoMessage = { role: 'user' | 'assistant'; text: string };

export function UserChat() {
  const [draft, setDraft] = useState('');
  const [messages, setMessages] = useState<DemoMessage[]>([]);
  const [provider, setProvider] = useState('codex');

  function sendLocalDemo(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const message = draft.trim();
    if (!message) return;
    setMessages((existing) => [
      ...existing,
      { role: 'user', text: message },
      { role: 'assistant', text: 'پاسخ نمایشی: هنوز هیچ درخواست واقعی ارسال نشده است. اتصال به Django و Providerها در مراحل بعدی فعال می‌شود.' },
    ]);
    setDraft('');
  }

  return (
    <div className="chat-workspace">
      <div className="chat-heading">
        <div>
          <span className="eyebrow">فضای گفتگو / پیش‌نمایش</span>
          <h1>دستیار هوشمند شما</h1>
        </div>
        <div className="model-selection">
          <label htmlFor="provider-select">ارائه‌دهنده نمونه</label>
          <select id="provider-select" value={provider} onChange={(event) => setProvider(event.target.value)}>
            <option value="codex">Codex</option>
            <option value="deepseek">DeepSeek</option>
            <option value="gemini">Gemini</option>
            <option value="qwen">Qwen</option>
            <option value="zai">Z.ai</option>
          </select>
          <span className="select-disabled" title="اتصال حساب در مراحل بعدی">
            حساب: اتصال‌داده‌نشده
          </span>
        </div>
      </div>
      {messages.length === 0 ? (
        <div className="chat-welcome">
          <div className="welcome-orb"><FontAwesomeIcon icon={faWandMagicSparkles} /></div>
          <h2>امروز می‌خواهید چه چیزی بسازید؟</h2>
          <p>یک مرکز برای گفتگو، کدنویسی، ارسال فایل و کار با مدل‌های گوناگون.</p>
          <div className="suggestion-grid">
            <button type="button" onClick={() => setDraft('معماری یک سرویس Django را پیشنهاد بده')}>معماری پروژه Django <span>↗</span></button>
            <button type="button" onClick={() => setDraft('یک رابط کاربری مدرن React طراحی کن')}>ایده‌پردازی رابط React <span>↗</span></button>
            <button type="button" onClick={() => setDraft('چگونه یک API چندرسانه‌ای طراحی کنم؟')}>طراحی API چندرسانه‌ای <span>↗</span></button>
          </div>
        </div>
      ) : (
        <div className="conversation" role="log" aria-label="گفتگوی آزمایشی">
          {messages.map((message, index) => (
            <div key={index} className={`message message-${message.role}`}>
              <div className="message-avatar">
                <FontAwesomeIcon icon={message.role === 'assistant' ? faRobot : faShieldHalved} />
              </div>
              <p>{message.text}</p>
            </div>
          ))}
        </div>
      )}
      <div className="chat-composer-wrap">
        <form className="chat-composer" onSubmit={sendLocalDemo}>
          <label className="sr-only" htmlFor="prompt-input">پیام شما</label>
          <textarea
            id="prompt-input"
            rows={2}
            value={draft}
            onChange={(event) => setDraft(event.target.value)}
            placeholder="پیامت را بنویس... (فقط پیش‌نمایش محلی)"
            onKeyDown={(event) => {
              if (event.key === 'Enter' && !event.shiftKey) {
                event.preventDefault();
                event.currentTarget.form?.requestSubmit();
              }
            }}
          />
          <div className="composer-actions">
            <button className="icon-button" type="button" disabled title="پیوست فایل در مراحل بعدی" aria-label="پیوست فایل (غیرفعال)">
              <FontAwesomeIcon icon={faPaperclip} />
            </button>
            <span className="muted-text">برای خط جدید Shift + Enter</span>
            <button className="send-button" type="submit" disabled={!draft.trim()} aria-label="ثبت پیام آزمایشی">
              <FontAwesomeIcon icon={faArrowUp} />
            </button>
          </div>
        </form>
        <p className="composer-caption">هیچ داده‌ای به سرور یا ارائه‌دهندگان ارسال نمی‌شود؛ گفتگوی آزمایشی فقط در حافظه همین صفحه است.</p>
      </div>
    </div>
  );
}

function SettingsPlaceholder({
  eyebrow,
  title,
  subtitle,
  icon,
  button,
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  icon: typeof faRobot;
  button: string;
}) {
  return (
    <div className="page-stack">
      <div className="page-heading">
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="panel empty-panel">
        <FontAwesomeIcon icon={icon} />
        <h2>هنوز داده‌ای برای نمایش وجود ندارد</h2>
        <p>ساخت، ذخیره و اتصال واقعی این بخش در مرحله مربوطه انجام می‌شود.</p>
        <button className="secondary-button" type="button" disabled>
          <FontAwesomeIcon icon={faPlus} /> {button}
        </button>
      </div>
    </div>
  );
}

export function UserAccounts() {
  return (
    <SettingsPlaceholder
      eyebrow="فضای کاری / حساب‌ها"
      title="حساب‌های من"
      subtitle="در آینده برای هر ارائه‌دهنده چند حساب مستقل با نشست‌های محفوظ و ورود دستی noVNC ثبت می‌کنید."
      icon={faCircleNodes}
      button="افزودن حساب"
    />
  );
}

export function UserTokens() {
  return (
    <SettingsPlaceholder
      eyebrow="فضای کاری / API"
      title="توکن‌های API"
      subtitle="توکن‌های اختصاصی با محدوده دسترسی به Providerها و حساب‌های منتخب از این قسمت مدیریت خواهند شد."
      icon={faKey}
      button="ایجاد توکن"
    />
  );
}

export function UploadPreview() {
  return (
    <div className="inline-note">
      <FontAwesomeIcon icon={faCloudArrowUp} /> آپلود و دانلود فایل پس از اتصال API جنگو فعال خواهد شد.
    </div>
  );
}
