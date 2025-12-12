import React, { useEffect, useState } from 'react';
import { useLocation } from '@docusaurus/router';
import PersonalizeButton from '../PersonalizeButton';

export default function ChapterPersonalize() {
  const location = useLocation();
  const [isChapterPage, setIsChapterPage] = useState(false);
  const [chapterPath, setChapterPath] = useState<string>('');

  useEffect(() => {
    // Check if we're on a chapter page (docs page)
    // Handle both with and without baseUrl
    const path = location.pathname;
    const baseUrl = '/PhysicalAI-Book/';
    
    // Remove baseUrl if present
    let normalizedPath = path;
    if (path.startsWith(baseUrl)) {
      normalizedPath = path.replace(baseUrl, '/');
    }
    
    const isDocsPage = normalizedPath.startsWith('/docs/') && 
                       normalizedPath !== '/docs/preface' &&
                       normalizedPath !== '/docs/preface/' &&
                       !normalizedPath.endsWith('/index') &&
                       !normalizedPath.endsWith('/index/') &&
                       normalizedPath !== '/docs/' &&
                       normalizedPath !== '/docs';
    
    setIsChapterPage(isDocsPage);
    
    if (isDocsPage) {
      const pathWithoutPrefix = normalizedPath.replace('/docs/', '').replace(/\/$/, '');
      setChapterPath(pathWithoutPrefix);
    }
  }, [location.pathname]);

  useEffect(() => {
    if (!isChapterPage || !chapterPath) return;

    // Use MutationObserver to watch for article element
    const observer = new MutationObserver(() => {
      const articleElement = document.querySelector('article');
      if (articleElement) {
        // Check if button already exists
        const existingButton = articleElement.querySelector('[data-personalize-button]');
        if (!existingButton && articleElement.children.length > 0) {
          // Small delay to ensure content is fully rendered
          setTimeout(() => {
            injectPersonalizeButton(articleElement, chapterPath);
          }, 300);
        }
      }
    });

    // Start observing
    observer.observe(document.body, {
      childList: true,
      subtree: true
    });

    // Also try immediately
    const articleElement = document.querySelector('article');
    if (articleElement && articleElement.children.length > 0) {
      const existingButton = articleElement.querySelector('[data-personalize-button]');
      if (!existingButton) {
        setTimeout(() => {
          injectPersonalizeButton(articleElement, chapterPath);
        }, 500);
      }
    }

    return () => observer.disconnect();
  }, [isChapterPage, chapterPath]);

  return null;
}

function injectPersonalizeButton(articleElement: Element, chapterPath: string) {
  // Check again if button exists
  if (articleElement.querySelector('[data-personalize-button]')) {
    return;
  }

  // Create container for button
  const buttonContainer = document.createElement('div');
  buttonContainer.setAttribute('data-personalize-button', 'true');
  buttonContainer.setAttribute('id', 'personalize-button-container');
  buttonContainer.style.cssText = `
    margin-bottom: 24px;
    margin-top: 16px;
    padding: 16px;
    background: var(--ifm-color-emphasis-100);
    border-radius: 8px;
    border: 1px solid var(--ifm-color-emphasis-200);
    width: 100%;
    box-sizing: border-box;
  `;

  // Create React root
  const root = document.createElement('div');
  buttonContainer.appendChild(root);

  // Find the first content element (skip header if exists)
  let insertPoint: Node | null = null;
  const firstChild = articleElement.firstElementChild;
  
  if (firstChild) {
    // If first child is header, insert after it
    if (firstChild.tagName === 'HEADER' || firstChild.classList.contains('theme-doc-header')) {
      insertPoint = firstChild.nextSibling;
    } else {
      // Otherwise insert at the very beginning
      insertPoint = firstChild;
    }
  } else {
    // No children, just append
    insertPoint = null;
  }

  // Insert the button container
  if (insertPoint) {
    articleElement.insertBefore(buttonContainer, insertPoint);
  } else {
    articleElement.insertBefore(buttonContainer, articleElement.firstChild);
  }

  // Get content for personalization
  const content = articleElement.innerText || articleElement.textContent || '';

  // Render button using React
  Promise.all([
    import('react'),
    import('react-dom/client')
  ]).then(([ReactModule, { createRoot }]) => {
    const React = ReactModule.default || ReactModule;
    const reactRoot = createRoot(root);
    reactRoot.render(
      React.createElement(PersonalizeButton, {
        chapterPath: chapterPath,
        content: content,
        onPersonalize: (personalizedContent: string) => {
          localStorage.setItem(`personalized_${chapterPath}`, personalizedContent);
          // Reload to show personalized content
          window.location.reload();
        }
      })
    );
  }).catch((error) => {
    console.error('Error rendering PersonalizeButton:', error);
    // Fallback: show a simple button
    root.innerHTML = `
      <button onclick="alert('Please refresh the page to enable personalization')" 
              style="padding: 10px 16px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                     color: white; border: none; border-radius: 8px; cursor: pointer;">
        ✨ Personalize
      </button>
    `;
  });
}

