import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import PersonalizeModal from '@site/src/components/PersonalizeModal';
import styles from './styles.module.css';
import { useApiUrl } from '@site/src/lib/api';

export default function ChapterPersonalize() {
  const apiUrl = useApiUrl();
  const baseUrl = useBaseUrl('/');
  const [user, setUser] = useState<any>(null);
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [isPersonalizing, setIsPersonalizing] = useState(false);
  const [showPersonalizeModal, setShowPersonalizeModal] = useState(false);
  const [personalizationLevel, setPersonalizationLevel] = useState('moderate');

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
    
    // Check if content is personalized
    const checkPersonalized = () => {
      const contentElement = document.querySelector('.markdown');
      if (contentElement && contentElement.dataset.originalContentForPersonalization) {
        setIsPersonalized(true);
      } else {
        setIsPersonalized(false);
      }
    };
    
    checkPersonalized();
    const interval = setInterval(checkPersonalized, 2000);
    return () => clearInterval(interval);
  }, []);

  const handlePersonalize = async (level?: string) => {
    if (!user) {
      alert('Please sign in to personalize content');
      window.location.href = `${baseUrl}auth/signin/`;
      return;
    }

    if (isPersonalized) {
      // Revert to original - restore from personalization original
      const contentElement = document.querySelector('.markdown');
      if (contentElement && contentElement.dataset.originalContentForPersonalization) {
        contentElement.innerHTML = contentElement.dataset.originalContentForPersonalization;
        delete contentElement.dataset.originalContentForPersonalization;
        setIsPersonalized(false);
        setShowPersonalizeModal(false); // Close modal if open
      }
      return;
    }

    // Show modal if level not provided
    if (!level) {
      setShowPersonalizeModal(true);
      return;
    }

    const contentElement = document.querySelector('.markdown');
    if (!contentElement) {
      alert('Content not found. Please navigate to a chapter page.');
      return;
    }

    setIsPersonalizing(true);
    const content = contentElement.textContent || '';
    
    if (!content || content.length < 100) {
      alert('Content is too short to personalize. Please navigate to a chapter with more content.');
      setIsPersonalizing(false);
      return;
    }

    const background = JSON.parse(localStorage.getItem('userBackground') || '{}');
    const chapterPath = typeof window !== 'undefined' ? window.location.pathname : '';

    try {
      // Store original content before personalizing (separate from translation)
      // Get true original - if translated, get from translation original, otherwise current
      if (!contentElement.dataset.originalContentForPersonalization) {
        const trueOriginal = contentElement.dataset.originalContentForTranslation 
          ? contentElement.dataset.originalContentForTranslation 
          : contentElement.innerHTML;
        contentElement.dataset.originalContentForPersonalization = trueOriginal;
      }

      const response = await fetch(`${apiUrl}/personalize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content,
          userBackground: background,
          chapterPath,
          personalizationLevel: level,
        }),
      });

      const data = await response.json();
      
      if (response.ok && data.personalizedContent) {
        contentElement.innerHTML = data.personalizedContent;
        setIsPersonalized(true);
        setPersonalizationLevel(level);
        setShowPersonalizeModal(false); // Close modal on success
        setIsPersonalizing(false); // Ensure button is not disabled
        // Scroll to top to show personalized content
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const errorMsg = data.detail || 'Failed to personalize content';
        alert(errorMsg);
        setShowPersonalizeModal(false); // Close modal on error
        setIsPersonalizing(false); // Ensure button is not disabled
        // Restore original if personalization failed
        if (contentElement.dataset.originalContentForPersonalization) {
          contentElement.innerHTML = contentElement.dataset.originalContentForPersonalization;
          delete contentElement.dataset.originalContentForPersonalization;
        }
      }
    } catch (error) {
      console.error('Personalization error:', error);
      alert('Network error. Please check if backend server is running.');
      setShowPersonalizeModal(false); // Close modal on error
      setIsPersonalizing(false); // Ensure button is not disabled
      // Restore original on error
      if (contentElement && contentElement.dataset.originalContentForPersonalization) {
        contentElement.innerHTML = contentElement.dataset.originalContentForPersonalization;
        delete contentElement.dataset.originalContentForPersonalization;
      }
    } finally {
      setIsPersonalizing(false); // Final safety check
    }
  };

  // Only show on docs pages - check with and without baseUrl
  const isDocsPage = typeof window !== 'undefined' && window.location.pathname.includes('/docs/');
  
  if (!isDocsPage) {
    return null;
  }

  return (
    <>
      <PersonalizeModal
        isOpen={showPersonalizeModal}
        onClose={() => setShowPersonalizeModal(false)}
        onConfirm={(level) => handlePersonalize(level)}
        currentLevel={personalizationLevel}
      />
      
      <div className={styles.personalizeContainer}>
        {!user ? (
          <div className={styles.signInPrompt}>
            <p>Sign in to personalize this content based on your background</p>
            <Link to="/auth/signin" className={styles.signInLink}>
              Sign In to Personalize
            </Link>
          </div>
        ) : (
          <button
            onClick={() => handlePersonalize()}
            className={`${styles.personalizeButton} ${isPersonalized ? styles.personalized : ''}`}
            disabled={isPersonalizing}
            type="button"
          >
            {isPersonalizing ? (
              <>
                <span className={styles.spinner} style={{ fontSize: '1.4rem', display: 'inline-block', lineHeight: '1', minWidth: '1.4rem', textAlign: 'center' }}>⏳</span>
                <span>Personalizing...</span>
              </>
            ) : isPersonalized ? (
              <>
                <span style={{ fontSize: '1.4rem', display: 'inline-block', lineHeight: '1', minWidth: '1.4rem', textAlign: 'center' }}>↩️</span>
                <span>Revert to Original</span>
              </>
            ) : (
              <>
                <span style={{ fontSize: '1.4rem', display: 'inline-block', lineHeight: '1', minWidth: '1.4rem', textAlign: 'center' }}>✨</span>
                <span>Personalize for Me</span>
              </>
            )}
          </button>
        )}
      </div>
    </>
  );
}

