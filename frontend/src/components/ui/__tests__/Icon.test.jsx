import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { Heart, Star, CheckCircle } from 'lucide-react';
import Icon from '../Icon';

describe('Icon Component', () => {
  it('renders icon with default props', () => {
    const { container } = render(<Icon icon={Heart} />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('returns null when no icon is provided', () => {
    const { container } = render(<Icon icon={null} />);

    expect(container.firstChild).toBeNull();
  });

  it('applies default size of 20', () => {
    const { container } = render(<Icon icon={Star} />);

    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('width', '20');
    expect(svg).toHaveAttribute('height', '20');
  });

  it('applies custom size', () => {
    const { container } = render(<Icon icon={Star} size={32} />);

    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('width', '32');
    expect(svg).toHaveAttribute('height', '32');
  });

  it('applies custom className', () => {
    const { container } = render(<Icon icon={CheckCircle} className="text-green-500" />);

    const svg = container.querySelector('svg');
    expect(svg).toHaveClass('text-green-500');
  });

  it('applies default strokeWidth of 1.75', () => {
    const { container } = render(<Icon icon={Heart} />);

    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('stroke-width', '1.75');
  });

  it('applies custom strokeWidth', () => {
    const { container } = render(<Icon icon={Heart} strokeWidth={2.5} />);

    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('stroke-width', '2.5');
  });

  it('has aria-hidden attribute for accessibility', () => {
    const { container } = render(<Icon icon={Star} />);

    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('aria-hidden', 'true');
  });

  it('renders different icon components correctly', () => {
    const { container: heartContainer } = render(<Icon icon={Heart} />);
    const { container: starContainer } = render(<Icon icon={Star} />);

    expect(heartContainer.querySelector('svg')).toBeInTheDocument();
    expect(starContainer.querySelector('svg')).toBeInTheDocument();

    // They should be different icons (different SVG content)
    expect(heartContainer.innerHTML).not.toBe(starContainer.innerHTML);
  });

  it('combines multiple props correctly', () => {
    const { container } = render(
      <Icon
        icon={CheckCircle}
        size={24}
        strokeWidth={2}
        className="text-blue-600 custom-class"
      />
    );

    const svg = container.querySelector('svg');
    expect(svg).toHaveAttribute('width', '24');
    expect(svg).toHaveAttribute('height', '24');
    expect(svg).toHaveAttribute('stroke-width', '2');
    expect(svg).toHaveClass('text-blue-600', 'custom-class');
    expect(svg).toHaveAttribute('aria-hidden', 'true');
  });
});
