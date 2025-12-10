import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import ChapterPersonalize from '@site/src/components/ChapterPersonalize';

/**
 * Wrapper component that uses createPortal to render ChapterPersonalize
 * into the chapter-personalize-container element while maintaining Router context
 */
function ChapterPersonalizePortal() {
  const [personalizeContainer, setPersonalizeContainer] = useState<HTMLElement | null>(null);

  useEffect(() => {
    // Find or create the chapter-personalize-container element
    const findOrCreateContainer = () => {
      // First, check if container already exists
      let container = document.getElementById('chapter-personalize-container');
      
      if (!container) {
        // Find the markdown content element
        const contentElement = document.querySelector('.markdown');
        if (contentElement) {
          // Create container at the start of markdown content
          container = document.createElement('div');
          container.id = 'chapter-personalize-container';
          contentElement.insertBefore(container, contentElement.firstChild);
        }
      }
      
      if (container) {
        setPersonalizeContainer(container);
      }
    };

    // Try immediately
    findOrCreateContainer();

    // Also try after multiple delays in case DOM isn't ready
    const timeout1 = setTimeout(findOrCreateContainer, 100);
    const timeout2 = setTimeout(findOrCreateContainer, 500);
    const timeout3 = setTimeout(findOrCreateContainer, 1000);

    // Use MutationObserver to watch for the element
    const observer = new MutationObserver(() => {
      const container = document.getElementById('chapter-personalize-container');
      if (container) {
        setPersonalizeContainer(container);
      } else {
        // Try to create it if markdown element exists
        const contentElement = document.querySelector('.markdown');
        const isDocsPage = window.location.pathname.includes('/docs/');
        if (contentElement && isDocsPage) {
          findOrCreateContainer();
        }
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });

    // Also check periodically
    const interval = setInterval(() => {
      const isDocsPage = window.location.pathname.includes('/docs/');
      if (isDocsPage) {
        const container = document.getElementById('chapter-personalize-container');
        if (!container) {
          findOrCreateContainer();
        }
      }
    }, 1000);

    return () => {
      clearTimeout(timeout1);
      clearTimeout(timeout2);
      clearTimeout(timeout3);
      clearInterval(interval);
      observer.disconnect();
    };
  }, []);

  if (!personalizeContainer) {
    return null;
  }

  return createPortal(<ChapterPersonalize />, personalizeContainer);
}

export default function ChapterPersonalizeWrapper() {
  // Only render on client side
  if (typeof window === 'undefined') {
    return null;
  }
  
  return <ChapterPersonalizePortal />;
}

