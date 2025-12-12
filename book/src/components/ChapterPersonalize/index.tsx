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
    if (!isChapterPage) return;

    const articleElement = document.querySelector('article');
    if (!articleElement) return;

    // Check if button already exists
    const existingButton = articleElement.querySelector('[data-personalize-button]');
    if (existingButton) return;

    // Wait for content to load
    const checkContent = setInterval(() => {
      const article = document.querySelector('article');
      if (article && article.children.length > 0) {
        clearInterval(checkContent);
        injectPersonalizeButton(article, chapterPath);
      }
    }, 100);

    return () => clearInterval(checkContent);
  }, [isChapterPage, chapterPath]);

  return null;
}

function injectPersonalizeButton(articleElement: Element, chapterPath: string) {
  // Check again if button exists
  if (articleElement.querySelector('[data-personalize-button]')) return;

  // Create container for button
  const buttonContainer = document.createElement('div');
  buttonContainer.setAttribute('data-personalize-button', 'true');
  buttonContainer.style.cssText = `
    margin-bottom: 24px;
    padding: 16px;
    background: var(--ifm-color-emphasis-100);
    border-radius: 8px;
    border: 1px solid var(--ifm-color-emphasis-200);
  `;

  // Create React root
  const root = document.createElement('div');
  buttonContainer.appendChild(root);

  // Insert at the beginning of article (after any existing header elements)
  const firstChild = articleElement.firstElementChild;
  if (firstChild && firstChild.tagName === 'HEADER') {
    // Insert after header
    articleElement.insertBefore(buttonContainer, firstChild.nextSibling);
  } else {
    // Insert at the beginning
    articleElement.insertBefore(buttonContainer, articleElement.firstChild);
  }

  // Get content for personalization
  const content = articleElement.innerText || articleElement.textContent || '';

  // Render button using React
  import('react-dom/client').then(({ createRoot }) => {
    const reactRoot = createRoot(root);
    reactRoot.render(
      <PersonalizeButton
        chapterPath={chapterPath}
        content={content}
        onPersonalize={(personalizedContent) => {
          localStorage.setItem(`personalized_${chapterPath}`, personalizedContent);
          // Reload to show personalized content
          window.location.reload();
        }}
      />
    );
  });
}

