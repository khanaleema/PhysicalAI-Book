import React, { useState, useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useApiUrl } from '@site/src/lib/api';
import styles from './styles.module.css';

const SUPPORTED_LANGUAGES = [
  { code: 'en', name: 'English', flag: '🇬🇧' },
  { code: 'ur', name: 'Urdu', flag: '🇵🇰' },
  { code: 'es', name: 'Spanish', flag: '🇪🇸' },
  { code: 'fr', name: 'French', flag: '🇫🇷' },
  { code: 'de', name: 'German', flag: '🇩🇪' },
  { code: 'ar', name: 'Arabic', flag: '🇸🇦' },
  { code: 'zh', name: 'Chinese', flag: '🇨🇳' },
  { code: 'ja', name: 'Japanese', flag: '🇯🇵' },
  { code: 'hi', name: 'Hindi', flag: '🇮🇳' },
  { code: 'pt', name: 'Portuguese', flag: '🇵🇹' },
];

export default function LanguageSwitcher() {
  const { i18n } = useTranslation();
  const apiUrl = useApiUrl();
  const [showDropdown, setShowDropdown] = useState(false);
  const [isTranslating, setIsTranslating] = useState(false);
  const currentLang = SUPPORTED_LANGUAGES.find(lang => lang.code === i18n.language) || SUPPORTED_LANGUAGES[0];

  const translatePage = async (targetLang: string) => {
    if (targetLang === i18n.language || isTranslating) return;
    
    setIsTranslating(true);
    setShowDropdown(false);

    try {
      // Get all text content from the page
      const contentElement = document.querySelector('.markdown') || document.querySelector('main');
      if (!contentElement) {
        console.error('Content element not found');
        setIsTranslating(false);
        return;
      }

      // Store original content if not already stored
      if (!contentElement.dataset.originalContent) {
        contentElement.dataset.originalContent = contentElement.innerHTML;
      }

      // Get text content for translation (extract from HTML)
      const textContent = contentElement.textContent || '';
      
      if (!textContent || textContent.length < 50) {
        console.error('Content too short to translate');
        setIsTranslating(false);
        return;
      }

      // Call translation API
      const response = await fetch(`${apiUrl}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: textContent,
          targetLanguage: targetLang,
          preserveFormatting: true,
        }),
      });

      const data = await response.json();
      
      if (response.ok && data.translatedContent) {
        // The translated content is already in markdown format
        // Parse it to HTML
        const { marked } = await import('marked');
        const htmlContent = marked.parse(data.translatedContent, {
          breaks: true,
          gfm: true,
        });
        
        // Replace content
        contentElement.innerHTML = htmlContent;
        i18n.changeLanguage(targetLang);
        localStorage.setItem('i18nextLng', targetLang);
        localStorage.setItem(`translated_content_${targetLang}`, htmlContent);
        
        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        console.error('Translation failed:', data.detail || 'Unknown error');
        alert('Translation failed. Please try again.');
      }
    } catch (error) {
      console.error('Translation error:', error);
      alert('Network error. Please check if backend server is running.');
    } finally {
      setIsTranslating(false);
    }
  };

  const revertToEnglish = () => {
    const contentElement = document.querySelector('.markdown') || document.querySelector('main');
    if (contentElement && contentElement.dataset.originalContent) {
      contentElement.innerHTML = contentElement.dataset.originalContent;
      delete contentElement.dataset.originalContent;
      i18n.changeLanguage('en');
      localStorage.setItem('i18nextLng', 'en');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  // Close dropdown on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showDropdown && !target.closest(`.${styles.languageSwitcher}`)) {
        setShowDropdown(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [showDropdown]);

  return (
    <div className={styles.languageSwitcher}>
      <button
        onClick={() => setShowDropdown(!showDropdown)}
        className={styles.languageButton}
        disabled={isTranslating}
        title="Change Language"
      >
        <span className={styles.flag}>{currentLang.flag}</span>
        <span className={styles.languageName}>
          {isTranslating ? 'Translating...' : currentLang.name}
        </span>
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </button>
      
      {showDropdown && (
        <>
          <div className={styles.dropdownOverlay} onClick={() => setShowDropdown(false)}></div>
          <div className={styles.dropdown}>
            {i18n.language !== 'en' && (
              <>
                <div 
                  className={`${styles.languageOption} ${styles.revertOption}`}
                  onClick={revertToEnglish}
                >
                  <span>🇬🇧</span>
                  <span>English (Original)</span>
                </div>
                <div className={styles.divider}></div>
              </>
            )}
            {SUPPORTED_LANGUAGES.map((lang) => (
              <div
                key={lang.code}
                className={`${styles.languageOption} ${i18n.language === lang.code ? styles.active : ''}`}
                onClick={() => translatePage(lang.code)}
              >
                <span>{lang.flag}</span>
                <span>{lang.name}</span>
                {i18n.language === lang.code && <span className={styles.checkmark}>✓</span>}
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  );
}

