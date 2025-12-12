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
  const [isLoading, setIsLoading] = useState(false);

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
      // Display personalized content
      displayPersonalizedContent(personalized, chapterPath);
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
    setIsLoading(true);
    try {
      // Store original content before personalizing
      const articleElement = document.querySelector('article');
      if (articleElement) {
        const originalContent = articleElement.innerHTML;
        localStorage.setItem(`original_${path}`, originalContent);
      }

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
          
          // Display personalized content
          displayPersonalizedContent(data.personalizedContent, path);
          
          // Call callback if provided
          if (onPersonalize) {
            onPersonalize(data.personalizedContent);
          }
        }
      } else {
        console.error('Personalization failed:', await response.text());
        alert('Failed to personalize content. Please try again.');
      }
    } catch (error) {
      console.error('Error personalizing content:', error);
      alert('Error personalizing content. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const displayPersonalizedContent = (personalizedMarkdown: string, path: string) => {
    const articleElement = document.querySelector('article');
    if (!articleElement) return;

    // Import marked to render markdown
    import('marked').then((markedModule) => {
      const marked = markedModule.default || markedModule;
      
      // Configure marked
      marked.setOptions({
        breaks: true,
        gfm: true,
      });

      // Convert markdown to HTML
      const htmlContent = marked.parse(personalizedMarkdown);
      
      // Find the main content area (skip header and button container)
      const buttonContainer = articleElement.querySelector('[data-personalize-button]');
      const header = articleElement.querySelector('header, .theme-doc-header');
      
      // Create a container for personalized content
      let contentContainer = articleElement.querySelector('[data-personalized-content]');
      if (!contentContainer) {
        contentContainer = document.createElement('div');
        contentContainer.setAttribute('data-personalized-content', 'true');
        contentContainer.style.cssText = 'margin-top: 24px;';
        
        // Insert after button container or header
        if (buttonContainer && buttonContainer.nextSibling) {
          articleElement.insertBefore(contentContainer, buttonContainer.nextSibling);
        } else if (header && header.nextSibling) {
          articleElement.insertBefore(contentContainer, header.nextSibling);
        } else {
          articleElement.insertBefore(contentContainer, articleElement.firstChild);
        }
      }
      
      // Hide original content (keep header and button)
      const originalContent = articleElement.querySelector('[data-original-content]');
      if (!originalContent) {
        // Wrap existing content (except button and header)
        const children = Array.from(articleElement.children);
        const wrapper = document.createElement('div');
        wrapper.setAttribute('data-original-content', 'true');
        wrapper.style.display = 'none';
        
        children.forEach((child) => {
          if (!child.hasAttribute('data-personalize-button') && 
              !child.hasAttribute('data-personalized-content') &&
              child.tagName !== 'HEADER' &&
              !child.classList.contains('theme-doc-header')) {
            wrapper.appendChild(child);
          }
        });
        
        if (wrapper.children.length > 0) {
          articleElement.appendChild(wrapper);
        }
      } else {
        originalContent.style.display = 'none';
      }
      
      // Display personalized content
      contentContainer.innerHTML = htmlContent;
      contentContainer.style.display = 'block';
    }).catch((error) => {
      console.error('Error loading marked:', error);
      // Fallback: just show as text
      const articleElement = document.querySelector('article');
      if (articleElement) {
        const contentContainer = articleElement.querySelector('[data-personalized-content]') || 
          document.createElement('div');
        contentContainer.setAttribute('data-personalized-content', 'true');
        contentContainer.textContent = personalizedMarkdown;
        contentContainer.style.cssText = 'margin-top: 24px; white-space: pre-wrap;';
        if (!articleElement.querySelector('[data-personalized-content]')) {
          articleElement.appendChild(contentContainer);
        }
      }
    });
  };

  const revertContent = (path: string) => {
    const articleElement = document.querySelector('article');
    if (!articleElement) return;

    // Remove personalized content
    const personalizedContent = articleElement.querySelector('[data-personalized-content]');
    if (personalizedContent) {
      personalizedContent.remove();
    }

    // Show original content
    const originalContent = articleElement.querySelector('[data-original-content]');
    if (originalContent) {
      originalContent.style.display = 'block';
      // Move children back to article
      const children = Array.from(originalContent.children);
      children.forEach((child) => {
        articleElement.appendChild(child);
      });
      originalContent.remove();
    } else {
      // Try to restore from localStorage
      const original = localStorage.getItem(`original_${path}`);
      if (original) {
        // This is a fallback - might not work perfectly
        window.location.reload();
      }
    }

    // Clear personalized content from localStorage
    localStorage.removeItem(`personalized_${path}`);
    setIsPersonalized(false);
  };

  // Check if user is logged in
  const isLoggedIn = typeof window !== 'undefined' && localStorage.getItem('user') !== null;

  return (
    <>
      <div style={{ display: 'flex', gap: '12px', alignItems: 'center', flexWrap: 'wrap' }}>
        <button
          className={styles.personalizeButton}
          onClick={handlePersonalize}
          disabled={isLoading}
          title={isPersonalized ? 'Content is personalized' : 'Personalize this chapter'}
        >
          <span className={styles.buttonIcon}>✨</span>
          <span className={styles.buttonText}>
            {isLoading ? 'Personalizing...' : isPersonalized ? 'Personalized for Me' : 'Personalize for Me'}
          </span>
          {userLevel && !isLoading && (
            <span className={styles.levelBadge}>{userLevel}</span>
          )}
        </button>
        
        {isPersonalized && (
          <button
            className={styles.revertButton}
            onClick={() => revertContent(chapterPath || '')}
            title="Revert to original content"
          >
            <span>↩️</span>
            <span>Revert</span>
          </button>
        )}
      </div>
      
      {!isLoggedIn && !isPersonalized && (
        <div style={{ 
          marginTop: '12px',
          padding: '12px 16px', 
          background: 'rgba(255, 255, 255, 0.1)', 
          borderRadius: '8px',
          fontSize: '13px',
          color: 'rgba(255, 255, 255, 0.9)',
          lineHeight: '1.5'
        }}>
          💡 <strong>Sign up</strong> to personalize content based on your learning level (Beginner, Intermediate, or Advanced)
        </div>
      )}
      
      <PersonalizeModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSelectLevel={handleLevelSelect}
        currentLevel={userLevel}
      />
    </>
  );
}

