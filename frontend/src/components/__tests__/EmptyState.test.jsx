import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Heart } from 'lucide-react';
import EmptyState from '../EmptyState';

describe('EmptyState Component', () => {
  it('renders with default icon and text', () => {
    render(
      <EmptyState
        title="Keine Ergebnisse"
        description="Es wurden keine Fördermöglichkeiten gefunden."
      />
    );

    expect(screen.getByText('Keine Ergebnisse')).toBeInTheDocument();
    expect(screen.getByText('Es wurden keine Fördermöglichkeiten gefunden.')).toBeInTheDocument();
  });

  it('renders with custom icon', () => {
    const { container } = render(
      <EmptyState
        icon={Heart}
        title="Custom Icon"
        description="This uses a custom icon"
      />
    );

    // The icon should be rendered
    expect(container.querySelector('svg')).toBeInTheDocument();
  });

  it('renders with action button', () => {
    const action = <button>Action Button</button>;

    render(
      <EmptyState
        title="Empty State"
        description="Some description"
        action={action}
      />
    );

    expect(screen.getByText('Action Button')).toBeInTheDocument();
  });

  it('applies correct CSS classes', () => {
    const { container } = render(
      <EmptyState
        title="Test Title"
        description="Test Description"
      />
    );

    const cardDiv = container.querySelector('.card');
    expect(cardDiv).toBeInTheDocument();
    expect(cardDiv).toHaveClass('animate-fade-in');
  });

  it('renders without action when not provided', () => {
    const { container } = render(
      <EmptyState
        title="No Action"
        description="This has no action"
      />
    );

    expect(container.querySelector('button')).not.toBeInTheDocument();
  });

  it('displays title and description in correct hierarchy', () => {
    render(
      <EmptyState
        title="Main Title"
        description="Supporting text below"
      />
    );

    const title = screen.getByText('Main Title');
    const description = screen.getByText('Supporting text below');

    expect(title.tagName).toBe('H3');
    expect(description.tagName).toBe('P');
  });
});
