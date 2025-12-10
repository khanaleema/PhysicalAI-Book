import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import { useApiUrl } from '@site/src/lib/api';

export default function ChapterTranslate() {
  const apiUrl = useApiUrl();
  const [user, setUser] = useState<any>(null);
  const [isTranslated, setIsTranslated] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
    
    // Check if content is translated
    const checkTranslated = () => {
      const contentElement = document.querySelector('.markdown');
      if (contentElement && contentElement.dataset.originalContent && contentElement.dataset.isUrdu) {
        setIsTranslated(true);
      } else {
        setIsTranslated(false);
      }
    };
    
    checkTranslated();
    const interval = setInterval(checkTranslated, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleTranslate = async () => {
    if (!user) {
      alert('Please sign in to translate content');
      window.location.href = '/auth/signin';
      return;
    }

    if (isTranslated) {
      // Revert to original
      const contentElement = document.querySelector('.markdown');
      if (contentElement && contentElement.dataset.originalContent) {
        contentElement.innerHTML = contentElement.dataset.originalContent;
        delete contentElement.dataset.originalContent;
        delete contentElement.dataset.isUrdu;
        setIsTranslated(false);
      }
      return;
    }

    const contentElement = document.querySelector('.markdown');
    if (!contentElement) {
      alert('Content not found. Please navigate to a chapter page.');
      return;
    }

    setIsTranslating(true);
    const content = contentElement.textContent || '';
    
    if (!content || content.length < 100) {
      alert('Content is too short to translate. Please navigate to a chapter with more content.');
      setIsTranslating(false);
      return;
    }

    const chapterPath = typeof window !== 'undefined' ? window.location.pathname : '';

    try {
      // Store original content before translating
      if (!contentElement.dataset.originalContent) {
        contentElement.dataset.originalContent = contentElement.innerHTML;
      }

      const response = await fetch(`${apiUrl}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          chapterPath,
          targetLanguage: 'urdu',
        }),
      });

      const data = await response.json();
      
      if (response.ok && data.translatedContent) {
        contentElement.innerHTML = data.translatedContent;
        contentElement.dataset.isUrdu = 'true';
        setIsTranslated(true);
        // Scroll to top to show translated content
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const errorMsg = data.detail || 'Failed to translate content';
        alert(errorMsg);
        // Restore original if translation failed
        if (contentElement.dataset.originalContent) {
          contentElement.innerHTML = contentElement.dataset.originalContent;
          delete contentElement.dataset.originalContent;
        }
      }
    } catch (error) {
      console.error('Translation error:', error);
      alert('Network error. Please check if backend server is running.');
      // Restore original on error
      if (contentElement && contentElement.dataset.originalContent) {
        contentElement.innerHTML = contentElement.dataset.originalContent;
        delete contentElement.dataset.originalContent;
      }
    } finally {
      setIsTranslating(false);
    }
  };

  // Only show on docs pages
  const isDocsPage = typeof window !== 'undefined' && window.location.pathname.startsWith('/docs/');
  
  if (!isDocsPage) {
    return null;
  }

  return (
    <div className={styles.translateContainer}>
      {!user ? (
        <div className={styles.signInPrompt}>
          <p>Sign in to translate this content to Urdu (اردو)</p>
          <Link to="/auth/signin" className={styles.signInLink}>
            Sign In to Translate
          </Link>
        </div>
      ) : (
        <button
          onClick={handleTranslate}
          className={`${styles.translateButton} ${isTranslated ? styles.translated : ''}`}
          disabled={isTranslating}
        >
          {isTranslating ? (
            <>
              <span className={styles.spinner}>⏳</span>
              <span>Translating to Urdu...</span>
            </>
          ) : isTranslated ? (
            <>
              <span>↩️</span>
              <span>Revert to English</span>
            </>
          ) : (
            <>
              <span>🌐</span>
              <span>Translate to Urdu (اردو)</span>
            </>
          )}
        </button>
      )}
    </div>
  );
}

