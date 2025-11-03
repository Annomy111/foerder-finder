import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import DismissibleBanner from '../DismissibleBanner';

describe('DismissibleBanner Component', () => {
  beforeEach(() => {
    // Clear localStorage before each test
    localStorage.clear();
  });

  it('renders banner content initially', () => {
    render(
      <DismissibleBanner id="test-banner">
        <div>Banner Content</div>
      </DismissibleBanner>
    );

    expect(screen.getByText('Banner Content')).toBeInTheDocument();
  });

  it('renders with custom className', () => {
    const { container } = render(
      <DismissibleBanner id="test-banner" className="custom-class">
        <div>Content</div>
      </DismissibleBanner>
    );

    const bannerDiv = container.querySelector('.custom-class');
    expect(bannerDiv).toBeInTheDocument();
  });

  it('renders function as children with close handler', () => {
    render(
      <DismissibleBanner id="test-banner">
        {({ close }) => (
          <div>
            <p>Content</p>
            <button onClick={close}>Close Banner</button>
          </div>
        )}
      </DismissibleBanner>
    );

    expect(screen.getByText('Content')).toBeInTheDocument();
    expect(screen.getByText('Close Banner')).toBeInTheDocument();
  });

  it('closes banner when close function is called', async () => {
    const user = userEvent.setup();

    render(
      <DismissibleBanner id="test-banner">
        {({ close }) => (
          <div>
            <p>Closable Content</p>
            <button onClick={close}>Close</button>
          </div>
        )}
      </DismissibleBanner>
    );

    const closeButton = screen.getByText('Close');
    expect(screen.getByText('Closable Content')).toBeInTheDocument();

    await user.click(closeButton);

    await waitFor(() => {
      expect(screen.queryByText('Closable Content')).not.toBeInTheDocument();
    });
  });

  it('saves dismiss state to localStorage', async () => {
    const user = userEvent.setup();

    render(
      <DismissibleBanner id="test-banner-123">
        {({ close }) => (
          <button onClick={close}>Dismiss</button>
        )}
      </DismissibleBanner>
    );

    const dismissButton = screen.getByText('Dismiss');
    await user.click(dismissButton);

    expect(localStorage.getItem('banner:test-banner-123')).toBe('hidden');
  });

  it('uses custom storageKeyPrefix', async () => {
    const user = userEvent.setup();

    render(
      <DismissibleBanner id="my-banner" storageKeyPrefix="custom">
        {({ close }) => (
          <button onClick={close}>Close</button>
        )}
      </DismissibleBanner>
    );

    const closeButton = screen.getByText('Close');
    await user.click(closeButton);

    expect(localStorage.getItem('custom:my-banner')).toBe('hidden');
  });

  it('does not render when previously dismissed', () => {
    // Pre-set localStorage to hidden
    localStorage.setItem('banner:dismissed-banner', 'hidden');

    render(
      <DismissibleBanner id="dismissed-banner">
        <div>Should not appear</div>
      </DismissibleBanner>
    );

    // Wait for useEffect to run
    waitFor(() => {
      expect(screen.queryByText('Should not appear')).not.toBeInTheDocument();
    });
  });

  it('renders when not previously dismissed', () => {
    // Ensure localStorage is empty
    expect(localStorage.getItem('banner:new-banner')).toBeNull();

    render(
      <DismissibleBanner id="new-banner">
        <div>Should appear</div>
      </DismissibleBanner>
    );

    expect(screen.getByText('Should appear')).toBeInTheDocument();
  });

  it('handles different banner IDs independently', async () => {
    const user = userEvent.setup();

    // Render first banner
    const { unmount: unmount1 } = render(
      <DismissibleBanner id="banner-1">
        {({ close }) => <button onClick={close}>Close 1</button>}
      </DismissibleBanner>
    );

    const close1Button = screen.getByText('Close 1');
    await user.click(close1Button);

    expect(localStorage.getItem('banner:banner-1')).toBe('hidden');

    // Unmount first banner
    unmount1();

    // Render a different banner with different ID
    render(
      <DismissibleBanner id="banner-2">
        <div>Banner 2 Content</div>
      </DismissibleBanner>
    );

    // Banner 2 should still be visible (different ID = not dismissed)
    expect(screen.getByText('Banner 2 Content')).toBeInTheDocument();
    expect(localStorage.getItem('banner:banner-2')).toBeNull();
  });

  it('handles localStorage errors gracefully', () => {
    // Mock localStorage to throw errors
    const originalGetItem = localStorage.getItem;
    const originalSetItem = localStorage.setItem;

    localStorage.getItem = () => {
      throw new Error('Storage not available');
    };
    localStorage.setItem = () => {
      throw new Error('Storage not available');
    };

    // Should not crash
    const { container } = render(
      <DismissibleBanner id="error-banner">
        {({ close }) => (
          <button onClick={close}>Close</button>
        )}
      </DismissibleBanner>
    );

    expect(container.querySelector('button')).toBeInTheDocument();

    // Restore original methods
    localStorage.getItem = originalGetItem;
    localStorage.setItem = originalSetItem;
  });

  it('updates correctly when id prop changes', async () => {
    const { rerender } = render(
      <DismissibleBanner id="banner-v1">
        <div>Version 1</div>
      </DismissibleBanner>
    );

    expect(screen.getByText('Version 1')).toBeInTheDocument();

    // Change the ID
    rerender(
      <DismissibleBanner id="banner-v2">
        <div>Version 2</div>
      </DismissibleBanner>
    );

    await waitFor(() => {
      expect(screen.getByText('Version 2')).toBeInTheDocument();
    });
  });

  it('renders element children correctly', () => {
    render(
      <DismissibleBanner id="element-banner">
        <div className="banner-content">
          <h3>Title</h3>
          <p>Description</p>
        </div>
      </DismissibleBanner>
    );

    expect(screen.getByText('Title')).toBeInTheDocument();
    expect(screen.getByText('Description')).toBeInTheDocument();
  });
});
