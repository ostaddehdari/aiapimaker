import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { describe, expect, it } from 'vitest';
import { LoginPage } from './LoginPage';

describe('LoginPage', () => {
  it('does not advertise an active authentication backend', () => {
    render(<MemoryRouter><LoginPage /></MemoryRouter>);
    expect(screen.getByRole('button', { name: /ورود به حساب/ })).toBeDisabled();
    expect(screen.getByRole('link', { name: /داشبورد مدیر/ })).toHaveAttribute('href', '/admin');
    expect(screen.getByRole('link', { name: /داشبورد کاربر/ })).toHaveAttribute('href', '/app');
    expect(screen.getByText(/پیش‌نمایش بدون احراز هویت/)).toBeInTheDocument();
  });
});
