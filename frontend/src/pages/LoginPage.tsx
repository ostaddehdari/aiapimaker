import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faArrowLeft,
  faArrowRightToBracket,
  faCircleCheck,
  faLock,
  faRobot,
  faShieldHalved,
} from '@fortawesome/free-solid-svg-icons';
import { Brand } from '../components/Brand';

export function LoginPage() {
  return (
    <div className="auth-page">
      <div className="auth-ambient ambient-one" aria-hidden="true" />
      <div className="auth-ambient ambient-two" aria-hidden="true" />
      <div className="auth-intro">
        <Brand />
        <div className="auth-message">
          <div className="hero-tag"><FontAwesomeIcon icon={faRobot} /> پلتفرم یکپارچه عامل‌های هوشمند</div>
          <h1>تمام مدل‌ها و حساب‌های هوش مصنوعی، <em>در یک فضای کاری.</em></h1>
          <p>
            مدیریت ارائه‌دهندگان، حساب‌های مستقل، گفتگوها، APIها و صف پردازش در بستری
            فارسی و توسعه‌پذیر.
          </p>
          <div className="auth-feature"><FontAwesomeIcon icon={faCircleCheck} /> پنل مستقل مدیریت و کاربر</div>
          <div className="auth-feature"><FontAwesomeIcon icon={faCircleCheck} /> حفاظت از نشست‌ها و حساب‌های متعدد</div>
          <div className="auth-feature"><FontAwesomeIcon icon={faCircleCheck} /> مسیر استقرار مستقل از دامنه</div>
        </div>
        <span className="auth-footer">AI API Maker • UI Foundation • Stage 05</span>
      </div>
      <div className="auth-form-column">
        <div className="auth-card">
          <div className="auth-card-icon"><FontAwesomeIcon icon={faLock} /></div>
          <span className="eyebrow">خوش آمدید</span>
          <h2>ورود به سامانه</h2>
          <p>در این مرحله فقط می‌توان ظاهر دو داشبورد را آزمایش کرد. ورود واقعی در Stage 09 فعال می‌شود.</p>
          <label className="input-label" htmlFor="username">نام کاربری</label>
          <input id="username" type="text" placeholder="نام کاربری" autoComplete="off" disabled />
          <label className="input-label" htmlFor="password">رمز عبور</label>
          <input id="password" type="password" placeholder="رمز عبور" autoComplete="off" disabled />
          <button className="primary-button full-width" type="button" disabled>
            <FontAwesomeIcon icon={faArrowRightToBracket} /> ورود به حساب
          </button>
          <div className="auth-divider"><span>پیش‌نمایش بدون احراز هویت</span></div>
          <div className="preview-links">
            <Link className="preview-link" to="/admin">
              <FontAwesomeIcon icon={faShieldHalved} />
              <span>داشبورد مدیر</span>
              <FontAwesomeIcon icon={faArrowLeft} className="link-arrow" />
            </Link>
            <Link className="preview-link" to="/app">
              <FontAwesomeIcon icon={faRobot} />
              <span>داشبورد کاربر</span>
              <FontAwesomeIcon icon={faArrowLeft} className="link-arrow" />
            </Link>
          </div>
          <small className="auth-note">این لینک‌ها تنها برای مشاهده رابط کاربری هستند و دسترسی مدیریتی واقعی ایجاد نمی‌کنند.</small>
        </div>
      </div>
    </div>
  );
}
