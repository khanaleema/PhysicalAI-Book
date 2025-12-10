import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import NavbarActions from '@site/src/components/NavbarActions';

/**
 * Wrapper component that uses createPortal to render NavbarActions
 * into the navbar-actions-root element while maintaining Router context
 */
function NavbarActionsPortal() {
  const [actionsRoot, setActionsRoot] = useState<HTMLElement | null>(null);

  useEffect(() => {
    // Find the navbar-actions-root element
    const findRoot = () => {
      const root = document.getElementById('navbar-actions-root');
      if (root) {
        setActionsRoot(root);
      }
    };

    // Try immediately
    findRoot();

    // Also try after multiple delays in case DOM isn't ready
    const timeout1 = setTimeout(findRoot, 100);
    const timeout2 = setTimeout(findRoot, 500);
    const timeout3 = setTimeout(findRoot, 1000);

    // Use MutationObserver to watch for the element
    const observer = new MutationObserver(findRoot);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    return () => {
      clearTimeout(timeout1);
      clearTimeout(timeout2);
      clearTimeout(timeout3);
      observer.disconnect();
    };
  }, []);

  if (!actionsRoot) {
    return null;
  }

  return createPortal(<NavbarActions />, actionsRoot);
}

export default function NavbarActionsWrapper() {
  // Only render on client side
  if (typeof window === 'undefined') {
    return null;
  }
  
  return <NavbarActionsPortal />;
}

