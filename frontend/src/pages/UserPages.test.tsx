import { fireEvent, render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { UserChat } from './UserPages';

describe('UserChat Stage 05 preview', () => {
  it('only adds a clearly labeled local demo response', () => {
    render(<UserChat />);
    const editor = screen.getByLabelText('پیام شما');
    fireEvent.change(editor, { target: { value: 'سلام' } });
    fireEvent.click(screen.getByRole('button', { name: /ثبت پیام آزمایشی/ }));
    expect(screen.getByText('سلام')).toBeInTheDocument();
    expect(screen.getByText(/هنوز هیچ درخواست واقعی ارسال نشده است/)).toBeInTheDocument();
  });
});
