import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import styles from './styles.module.css';
import { useApiUrl } from '@site/src/lib/api';

interface PersonalizeButtonProps {
  chapterPath: string;
  originalContent: string;
}

export default function PersonalizeButton({ chapterPath, originalContent }: PersonalizeButtonProps) {
  const apiUrl = useApiUrl();
  const [isPersonalized, setIsPersonalized] = useState(false);
  const [loading, setLoading] = useState(false);
  const [user, setUser] = useState<any>(null);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
  }, []);

  const handlePersonalize = async () => {
    if (!user) {
      alert('Please sign in to personalize content');
      window.location.href = '/auth/signin';
      return;
    }

    setLoading(true);
    try {
      const background = JSON.parse(localStorage.getItem('userBackground') || '{}');
      
      const response = await fetch(`${apiUrl}/personalize`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          content: originalContent,
          userBackground: background,
          chapterPath,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        // Replace content in the page
        const contentElement = document.querySelector('.markdown');
        if (contentElement && data.personalizedContent) {
          contentElement.innerHTML = data.personalizedContent;
          setIsPersonalized(true);
        }
      }
    } catch (error) {
      console.error('Personalization error:', error);
      alert('Failed to personalize content. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return (
      <div className={styles.personalizeContainer}>
        <Link to="/auth/signin" className={styles.signInPrompt}>
          Sign in to personalize this content
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.personalizeContainer}>
      <button
        onClick={handlePersonalize}
        disabled={loading || isPersonalized}
        className={`${styles.personalizeButton} ${isPersonalized ? styles.personalized : ''}`}
        style={{ width: '100%' }}
      >
        {loading ? (
          <span>⏳ Personalizing...</span>
        ) : isPersonalized ? (
          <span>✓ Content Personalized</span>
        ) : (
          <span>🎯 Personalize Content</span>
        )}
      </button>
      {isPersonalized && (
        <p className={styles.hint}>
          Content has been personalized based on your background
        </p>
      )}
    </div>
  );
}

