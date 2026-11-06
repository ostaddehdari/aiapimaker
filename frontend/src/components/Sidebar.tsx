import { useEffect, useRef, useState } from 'react';
import { NavLink } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import {
  faBars,
  faChartLine,
  faComments,
  faHouse,
  faKey,
  faLayerGroup,
  faPlus,
  faRightFromBracket,
  faRobot,
  faUsers,
  faXmark,
} from '@fortawesome/free-solid-svg-icons';
import { gsap } from 'gsap';
import type { IconDefinition } from '@fortawesome/fontawesome-svg-core';
import { Brand } from './Brand';

export type ShellRole = 'admin' | 'user';
type SidebarProps = {
  role: ShellRole;
  onCollapseChange?: (collapsed: boolean) => void;
};

type NavItem = { path: string; title: string; icon: IconDefinition; end?: boolean };

const adminItems: NavItem[] = [
  { path: '/admin', title: 'نمای کلی', icon: faHouse, end: true },
  { path: '/admin/providers', title: 'ارائه‌دهندگان', icon: faLayerGroup },
  { path: '/admin/users', title: 'مدیریت کاربران', icon: faUsers },
  { path: '/admin/supervisor', title: 'سوپروایزر و مانیتورینگ', icon: faChartLine },
];

const userItems: NavItem[] = [
  { path: '/app', title: 'گفتگوها', icon: faComments, end: true },
  { path: '/app/accounts', title: 'حساب‌های من', icon: faRobot },
  { path: '/app/api-tokens', title: 'توکن‌های API', icon: faKey },
];

export function Sidebar({ role, onCollapseChange }: SidebarProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const sidebarRef = useRef<HTMLElement>(null);
  const menuId = `sidebar-${role}`;
  const items = role === 'admin' ? adminItems : userItems;

  useEffect(() => {
    const sidebar = sidebarRef.current;
    if (!sidebar) return;
    const width = collapsed ? 84 : 270;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (reduceMotion) {
      sidebar.style.width = `${width}px`;
      return;
    }
    const tween = gsap.to(sidebar, { width, duration: 0.36, ease: 'power2.inOut' });
    return () => {
      tween.kill();
    };
  }, [collapsed]);

  const toggle = () => {
    setCollapsed((previous) => {
      onCollapseChange?.(!previous);
      return !previous;
    });
  };
  const closeMobile = () => setMobileOpen(false);

  return (
    <>
      <button
        className="mobile-menu-button icon-button"
        type="button"
        aria-controls={menuId}
        aria-expanded={mobileOpen}
        aria-label="باز کردن فهرست"
        onClick={() => setMobileOpen(true)}
      >
        <FontAwesomeIcon icon={faBars} />
      </button>
      {mobileOpen && (
        <button
          className="mobile-backdrop"
          onClick={closeMobile}
          type="button"
          aria-label="بستن فهرست"
        />
      )}
      <aside
        ref={sidebarRef}
        id={menuId}
        className={`shell-sidebar ${collapsed ? 'collapsed' : ''} ${mobileOpen ? 'mobile-open' : ''}`}
        aria-label={role === 'admin' ? 'منوی مدیریت' : 'منوی کاربر'}
      >
        <div className="sidebar-top">
          <Brand compact={collapsed} />
          <button className="icon-button collapse-toggle" onClick={toggle} type="button"
            title={collapsed ? 'باز کردن سایدبار' : 'جمع کردن سایدبار'}
            aria-label={collapsed ? 'باز کردن سایدبار' : 'جمع کردن سایدبار'}>
            <FontAwesomeIcon icon={faBars} />
          </button>
          <button className="icon-button mobile-close" type="button" aria-label="بستن فهرست" onClick={closeMobile}>
            <FontAwesomeIcon icon={faXmark} />
          </button>
        </div>
        <div className="sidebar-divider" />
        {role === 'user' && (
          <NavLink className="new-chat-button" to="/app" onClick={closeMobile} title="گفتگوی جدید">
            <FontAwesomeIcon icon={faPlus} />
            <span className="sidebar-label">گفتگوی جدید</span>
          </NavLink>
        )}
        <p className="sidebar-section-title sidebar-label">{role === 'admin' ? 'مدیریت سامانه' : 'فضای کاری من'}</p>
        <nav className="sidebar-nav">
          {items.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              end={item.end}
              onClick={closeMobile}
              title={item.title}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              <FontAwesomeIcon icon={item.icon} />
              <span className="sidebar-label">{item.title}</span>
            </NavLink>
          ))}
        </nav>
        {role === 'user' && (
          <div className="history-group">
            <p className="sidebar-section-title sidebar-label">گفتگوهای اخیر</p>
            <p className="sidebar-helper sidebar-label">پس از اتصال API، گفتگوها اینجا ذخیره می‌شوند.</p>
          </div>
        )}
        <div className="sidebar-spacer" />
        <div className="sidebar-bottom">
          <NavLink to="/login" className="nav-item" onClick={closeMobile}>
            <FontAwesomeIcon icon={faRightFromBracket} />
            <span className="sidebar-label">بازگشت به ورود آزمایشی</span>
          </NavLink>
          <div className="sidebar-build sidebar-label">Stage 05 • رابط کاربری نمایشی</div>
        </div>
      </aside>
    </>
  );
}
