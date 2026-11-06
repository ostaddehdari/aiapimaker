import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Brand } from './Brand';

describe('Brand', () => {
  it('renders an accessible product identity', () => {
    render(<Brand />);
    expect(screen.getByLabelText('AI API Maker')).toBeInTheDocument();
    expect(screen.getByText('درگاه هوش مصنوعی')).toBeInTheDocument();
  });
});
