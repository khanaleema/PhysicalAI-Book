import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';
import PersonalizeModal from '../PersonalizeModal';

interface PersonalizeButtonProps {
  chapterPath?: string;
  content?: string;
  onPersonalize?: (personalizedContent: string) => void;
}

export default function PersonalizeButton({ 
  chapterPath, 
  content,
  onPersonalize 
}: PersonalizeButtonProps) {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [userLevel, setUserLevel] = useState<string | null>(null);
  const [isPersonalized, setIsPersonalized] = useState(false);

  useEffect(() => {
    // Load user level from localStorage
    const savedLevel = localStorage.getItem('user_level');
    if (savedLevel) {
      setUserLevel(savedLevel);
    }
    
    // Check if content is already personalized
    const personalized = localStorage.getItem(`personalized_${chapterPath}`);
    if (personalized) {
      setIsPersonalized(true);
    }
  }, [chapterPath]);

  const handlePersonalize = () => {
    // If user already has a level and content is available, personalize directly
    if (userLevel && content && chapterPath && !isPersonalized) {
      personalizeContent(content, userLevel, chapterPath);
    } else {
      // Otherwise, open modal to select/change level
      setIsModalOpen(true);
    }
  };

  const handleLevelSelect = async (level: string) => {
    setUserLevel(level);
    localStorage.setItem('user_level', level);
    setIsModalOpen(false);
    
    // If content is provided, personalize it
    if (content && chapterPath) {
      await personalizeContent(content, level, chapterPath);
    }
  };

  const personalizeContent = async (content: string, level: string, path: string) => {
    try {
      const apiUrl = typeof window !== 'undefined' 
        ? (window as any).CHATBOT_API_URL || 'https://aleemakhan-ai-book-be.hf.space'
        : 'https://aleemakhan-ai-book-be.hf.space';

      const response = await fetch(`${apiUrl}/personalize`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          content,
          userLevel: level,
          chapterPath: path,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.personalizedContent) {
          // Store personalized content
          localStorage.setItem(`personalized_${path}`, data.personalizedContent);
          setIsPersonalized(true);
          
          // Call callback if provided
          if (onPersonalize) {
            onPersonalize(data.personalizedContent);
          }
          
          // Reload page to show personalized content
          window.location.reload();
        }
      } else {
        console.error('Personalization failed:', await response.text());
      }
    } catch (error) {
      console.error('Error personalizing content:', error);
    }
  };

  return (
    <>
      <button
        className={styles.personalizeButton}
        onClick={handlePersonalize}
        title={isPersonalized ? 'Content is personalized' : 'Personalize this chapter'}
      >
        <span className={styles.buttonIcon}>✨</span>
        <span className={styles.buttonText}>
          {isPersonalized ? 'Personalized' : 'Personalize'}
        </span>
        {userLevel && (
          <span className={styles.levelBadge}>{userLevel}</span>
        )}
      </button>
      
      <PersonalizeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSelectLevel={handleLevelSelect}
        currentLevel={userLevel}
      />
    </>
  );
}

