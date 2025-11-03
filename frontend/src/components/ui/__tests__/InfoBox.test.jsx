import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Info, CheckCircle } from 'lucide-react';
import InfoBox from '../InfoBox';

describe('InfoBox Component', () => {
  it('renders with default variant (info)', () => {
    render(
      <InfoBox>
        <p>This is an info message</p>
      </InfoBox>
    );

    expect(screen.getByText('This is an info message')).toBeInTheDocument();
  });

  it('renders with title', () => {
    render(
      <InfoBox title="Important Notice">
        <p>Content here</p>
      </InfoBox>
    );

    expect(screen.getByText('Important Notice')).toBeInTheDocument();
  });

  it('renders with icon', () => {
    const { container } = render(
      <InfoBox icon={Info} title="Info">
        <p>Content</p>
      </InfoBox>
    );

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('applies info variant classes', () => {
    const { container } = render(
      <InfoBox variant="info">
        <p>Info content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('bg-blue-50', 'border-blue-200', 'text-blue-800');
  });

  it('applies success variant classes', () => {
    const { container } = render(
      <InfoBox variant="success">
        <p>Success content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('bg-emerald-500/10', 'border-emerald-500/30', 'text-emerald-700');
  });

  it('applies warning variant classes', () => {
    const { container } = render(
      <InfoBox variant="warning">
        <p>Warning content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('bg-amber-100', 'border-amber-300', 'text-amber-800');
  });

  it('applies danger variant classes', () => {
    const { container } = render(
      <InfoBox variant="danger">
        <p>Danger content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('bg-red-100', 'border-red-300', 'text-red-800');
  });

  it('renders with actions', () => {
    const actions = (
      <>
        <button>Action 1</button>
        <button>Action 2</button>
      </>
    );

    render(
      <InfoBox actions={actions}>
        <p>Content with actions</p>
      </InfoBox>
    );

    expect(screen.getByText('Action 1')).toBeInTheDocument();
    expect(screen.getByText('Action 2')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <InfoBox className="custom-class">
        <p>Content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('custom-class');
  });

  it('has correct semantic role', () => {
    const { container } = render(
      <InfoBox>
        <p>Content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveAttribute('role', 'status');
  });

  it('renders without icon when not provided', () => {
    const { container } = render(
      <InfoBox title="No Icon">
        <p>Content</p>
      </InfoBox>
    );

    const iconWrapper = container.querySelector('.rounded-2xl.bg-white\\/60');
    expect(iconWrapper).not.toBeInTheDocument();
  });

  it('renders without title when not provided', () => {
    render(
      <InfoBox>
        <p>Content without title</p>
      </InfoBox>
    );

    const heading = document.querySelector('h3');
    expect(heading).not.toBeInTheDocument();
  });

  it('has animation class', () => {
    const { container } = render(
      <InfoBox>
        <p>Animated content</p>
      </InfoBox>
    );

    const section = container.querySelector('section');
    expect(section).toHaveClass('animate-fade-in');
  });

  it('renders complex children', () => {
    render(
      <InfoBox title="Complex Content">
        <div>
          <p>Paragraph 1</p>
          <ul>
            <li>Item 1</li>
            <li>Item 2</li>
          </ul>
        </div>
      </InfoBox>
    );

    expect(screen.getByText('Paragraph 1')).toBeInTheDocument();
    expect(screen.getByText('Item 1')).toBeInTheDocument();
    expect(screen.getByText('Item 2')).toBeInTheDocument();
  });

  it('combines all props correctly', () => {
    const actions = <button>Close</button>;

    const { container } = render(
      <InfoBox
        title="Full Featured InfoBox"
        icon={CheckCircle}
        variant="success"
        actions={actions}
        className="my-custom-class"
      >
        <p>This has all props</p>
      </InfoBox>
    );

    const section = container.querySelector('section');

    // Check all elements are present
    expect(screen.getByText('Full Featured InfoBox')).toBeInTheDocument();
    expect(screen.getByText('This has all props')).toBeInTheDocument();
    expect(screen.getByText('Close')).toBeInTheDocument();
    expect(container.querySelector('svg')).toBeInTheDocument();

    // Check classes
    expect(section).toHaveClass(
      'bg-emerald-500/10',
      'border-emerald-500/30',
      'text-emerald-700',
      'my-custom-class',
      'animate-fade-in'
    );
  });
});
