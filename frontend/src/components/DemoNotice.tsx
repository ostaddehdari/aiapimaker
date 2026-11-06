import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCircleInfo } from '@fortawesome/free-solid-svg-icons';

export function DemoNotice() {
  return (
    <div className="demo-notice" role="status">
      <FontAwesomeIcon icon={faCircleInfo} />
      <span>
        این محیط پیش‌نمایش Stage 05 است. ورود، حساب‌ها، آمار و اتصال به مدل‌ها هنوز واقعی نیستند.
      </span>
    </div>
  );
}
