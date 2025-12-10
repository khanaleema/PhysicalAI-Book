import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';
import { useApiUrl } from '@site/src/lib/api';

interface TranslateButtonProps {
  chapterPath: string;
  originalContent: string;
}

export default function TranslateButton({ chapterPath, originalContent }: TranslateButtonProps) {
  const apiUrl = useApiUrl();
  const [isTranslated, setIsTranslated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [originalHtml, setOriginalHtml] = useState<string>('');

  useEffect(() => {
    // Store original HTML when component mounts or route changes
    const timer = setTimeout(() => {
      const contentElement = document.querySelector('.markdown');
      if (contentElement && !originalHtml) {
        setOriginalHtml(contentElement.innerHTML);
      }
    }, 500);
    
    return () => clearTimeout(timer);
  }, [chapterPath]);

  const handleTranslate = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/translate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: originalContent,
          targetLanguage: 'ur', // Urdu
          chapterPath,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        const contentElement = document.querySelector('.markdown');
        if (contentElement) {
          if (isTranslated) {
            // Restore original
            contentElement.innerHTML = originalHtml;
            setIsTranslated(false);
          } else {
            // Show translated
            if (data.translatedContent) {
              // Store original if not stored
              if (!originalHtml) {
                setOriginalHtml(contentElement.innerHTML);
              }
              contentElement.innerHTML = data.translatedContent;
              setIsTranslated(true);
            }
          }
        }
      } else {
        const errorMsg = data.detail || 'Failed to translate content';
        alert(errorMsg);
      }
    } catch (error) {
      console.error('Translation error:', error);
      alert('Failed to translate content. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.translateContainer}>
      <button
        onClick={handleTranslate}
        disabled={loading}
        className={`${styles.translateButton} ${isTranslated ? styles.translated : ''}`}
        style={{ width: '100%' }}
      >
        {loading ? (
          <span>⏳ Translating...</span>
        ) : isTranslated ? (
          <span>🔄 Show English</span>
        ) : (
          <span>🌐 Translate to Urdu (اردو)</span>
        )}
      </button>
      {isTranslated && (
        <p className={styles.hint}>
          Content is now in Urdu. Click to switch back to English.
        </p>
      )}
    </div>
  );
}

