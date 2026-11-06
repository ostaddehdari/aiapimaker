import { Outlet, useLocation } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faMoon, faSun, faShieldHalved } from '@fortawesome/free-solid-svg-icons';
import { useTheme } from '../theme';
import { DemoNotice } from './DemoNotice';
import { Sidebar } from './Sidebar';
import type { ShellRole } from './Sidebar';

export function AppShell({ role }: { role: ShellRole }) {
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();
  const isAdmin = role === 'admin';

  return (
    <div className="app-shell">
      <a href="#main-content" className="skip-link">رفتن به محتوای اصلی</a>
      <Sidebar role={role} />
      <div className="app-content">
        <header className="topbar">
          <div className="topbar-intro">
            <span className="eyebrow">{isAdmin ? 'پنل مدیریت' : 'فضای کاری هوشمند'}</span>
            <strong>{isAdmin ? 'مدیریت AI API Maker' : 'دستیار چندمدلی شما'}</strong>
          </div>
          <div className="topbar-actions">
            <span className="topbar-route" dir="ltr">{location.pathname}</span>
            <button className="icon-button theme-toggle" type="button" onClick={toggleTheme}
              aria-label={theme === 'dark' ? 'فعال‌کردن حالت روشن' : 'فعال‌کردن حالت تاریک'}
              title={theme === 'dark' ? 'حالت روشن' : 'حالت تاریک'}>
              <FontAwesomeIcon icon={theme === 'dark' ? faSun : faMoon} />
            </button>
            <div className="avatar" title="حساب نمایشی" aria-label="حساب نمایشی">
              <FontAwesomeIcon icon={faShieldHalved} />
            </div>
          </div>
        </header>
        <main id="main-content" className="workspace-main" tabIndex={-1}>
          <DemoNotice />
          <Outlet />
        </main>
      </div>
    </div>
  );
}
