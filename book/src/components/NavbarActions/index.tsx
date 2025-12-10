import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';
import { marked } from 'marked';
import { useApiUrl } from '@site/src/lib/api';

export default function NavbarActions() {
  const apiUrl = useApiUrl();
  const baseUrl = useBaseUrl('/');
  const [user, setUser] = useState<any>(null);
  const [showMenu, setShowMenu] = useState(false);
  const [isUrdu, setIsUrdu] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
    
    // Check if content is translated
    const checkUrdu = () => {
      const contentElement = document.querySelector('.markdown');
      if (contentElement && contentElement.dataset.isUrdu) {
        setIsUrdu(true);
      } else {
        setIsUrdu(false);
      }
    };
    
    checkUrdu();
    const interval = setInterval(checkUrdu, 2000);
    
    // Close dropdown on outside click
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showMenu && !target.closest(`.${styles.userMenuContainer}`)) {
        setShowMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    
    return () => {
      clearInterval(interval);
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showMenu]);

  const handleTranslate = async () => {
    if (!user) {
      alert('Please sign in to translate content');
      window.location.href = '/auth/signin';
      return;
    }

    const contentElement = document.querySelector('.markdown');
    if (!contentElement) {
      alert('Content not found. Please navigate to a chapter page.');
      return;
    }

    if (isUrdu) {
      // Revert to English - restore from translation original
      if (contentElement.dataset.originalContentForTranslation) {
        contentElement.innerHTML = contentElement.dataset.originalContentForTranslation;
        delete contentElement.dataset.originalContentForTranslation;
        delete contentElement.dataset.isUrdu;
        setIsUrdu(false);
      }
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
      // Store original content before translating (separate from personalization)
      // Use a different dataset key to avoid conflicts with personalization
      if (!contentElement.dataset.originalContentForTranslation) {
        // Get the true original - if personalized, get from personalized original, otherwise current
        const trueOriginal = contentElement.dataset.originalContentForPersonalization 
          ? contentElement.dataset.originalContentForPersonalization 
          : contentElement.innerHTML;
        contentElement.dataset.originalContentForTranslation = trueOriginal;
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
        // Convert markdown to HTML for proper rendering
        const htmlContent = marked.parse(data.translatedContent, {
          breaks: true,
          gfm: true,
        });
        contentElement.innerHTML = htmlContent;
        contentElement.dataset.isUrdu = 'true';
        setIsUrdu(true);
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        const errorMsg = data.detail || 'Failed to translate content';
        alert(errorMsg);
        if (contentElement.dataset.originalContentForTranslation) {
          contentElement.innerHTML = contentElement.dataset.originalContentForTranslation;
          delete contentElement.dataset.originalContentForTranslation;
        }
      }
    } catch (error) {
      console.error('Translation error:', error);
      alert('Network error. Please check if backend server is running.');
      if (contentElement && contentElement.dataset.originalContentForTranslation) {
        contentElement.innerHTML = contentElement.dataset.originalContentForTranslation;
        delete contentElement.dataset.originalContentForTranslation;
      }
    } finally {
      setIsTranslating(false);
    }
  };

  const handleSignOut = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('userBackground');
    localStorage.removeItem('authToken');
    setUser(null);
    setShowMenu(false);
    // Redirect to home page with baseUrl
    window.location.href = baseUrl;
  };

  // Check if we're on a docs page - check with and without baseUrl
  const isDocsPage = typeof window !== 'undefined' && window.location.pathname.includes('/docs/');

  return (
    <div className={styles.navbarActions}>
      {/* Language Toggle - Only show on docs pages */}
      {isDocsPage && user && (
        <button
          onClick={handleTranslate}
          className={`${styles.languageToggle} ${isUrdu ? styles.active : ''}`}
          disabled={isTranslating}
          title={isUrdu ? 'Switch to English' : 'Translate to Urdu (اردو)'}
        >
          <span className={styles.languageIcon}>
            {isUrdu ? '🇬🇧' : '🇵🇰'}
          </span>
          <span className={styles.languageText}>
            {isTranslating ? 'Translating...' : isUrdu ? 'English' : 'اردو'}
          </span>
        </button>
      )}

      {/* User Menu */}
      {!user ? (
        <>
          <Link to="/auth/signin" className={styles.signInButton}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
              <polyline points="10 17 15 12 10 7"></polyline>
              <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            <span>Sign In</span>
          </Link>
          <Link to="/auth/signup" className={styles.signUpButton}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <line x1="20" y1="8" x2="20" y2="14"></line>
              <line x1="23" y1="11" x2="17" y2="11"></line>
            </svg>
            <span>Sign Up</span>
          </Link>
        </>
      ) : (
        <div className={styles.userMenuContainer}>
          <button 
            className={styles.userInfo} 
            onClick={() => setShowMenu(!showMenu)}
            aria-label="User menu"
          >
            <div className={styles.avatar}>
              {user.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          {showMenu && (
            <>
              <div className={styles.dropdownOverlay} onClick={() => setShowMenu(false)}></div>
              <div className={styles.dropdown}>
                <div className={styles.dropdownHeader}>
                  <div className={styles.dropdownAvatar}>
                    {user.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div>
                    <strong>{user.name}</strong>
                    <div className={styles.email}>{user.email}</div>
                  </div>
                </div>
                <div className={styles.divider}></div>
                <Link to="/auth/profile" className={styles.dropdownItem} onClick={() => setShowMenu(false)}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  <span>Edit Profile</span>
                </Link>
                <div className={styles.divider}></div>
                <div className={styles.dropdownItem} onClick={handleSignOut}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  <span>Sign Out</span>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}

