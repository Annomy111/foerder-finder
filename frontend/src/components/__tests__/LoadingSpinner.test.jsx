import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('renders with default props', () => {
    render(<LoadingSpinner />);

    expect(screen.getByText('Lädt...')).toBeInTheDocument();
  });

  it('renders with custom text', () => {
    render(<LoadingSpinner text="Bitte warten..." />);

    expect(screen.getByText('Bitte warten...')).toBeInTheDocument();
  });

  it('renders without text when text is empty string', () => {
    const { container } = render(<LoadingSpinner text="" />);

    expect(container.querySelector('p')).not.toBeInTheDocument();
  });

  it('renders with small size', () => {
    const { container } = render(<LoadingSpinner size="sm" />);

    const spinner = container.querySelector('.w-4.h-4');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with medium size (default)', () => {
    const { container } = render(<LoadingSpinner size="md" />);

    const spinner = container.querySelector('.w-8.h-8');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with large size', () => {
    const { container } = render(<LoadingSpinner size="lg" />);

    const spinner = container.querySelector('.w-12.h-12');
    expect(spinner).toBeInTheDocument();
  });

  it('renders with extra large size', () => {
    const { container } = render(<LoadingSpinner size="xl" />);

    const spinner = container.querySelector('.w-16.h-16');
    expect(spinner).toBeInTheDocument();
  });

  it('has spinning animation', () => {
    const { container } = render(<LoadingSpinner />);

    const spinner = container.querySelector('.animate-spin');
    expect(spinner).toBeInTheDocument();
  });

  it('text has pulse animation', () => {
    const { container } = render(<LoadingSpinner text="Loading..." />);

    const text = container.querySelector('.animate-pulse');
    expect(text).toBeInTheDocument();
  });

  it('applies correct border styling', () => {
    const { container } = render(<LoadingSpinner />);

    const innerDiv = container.querySelector('.rounded-full.border-4');
    expect(innerDiv).toBeInTheDocument();
    expect(innerDiv).toHaveClass('border-gray-200');
    expect(innerDiv).toHaveClass('border-t-primary-600');
  });
});
