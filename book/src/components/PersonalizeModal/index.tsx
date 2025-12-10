import React, { useState, useEffect } from 'react';
import styles from './styles.module.css';

interface PersonalizeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: (level: string) => void;
  currentLevel?: string;
}

const personalizationLevels = [
  {
    value: 'light',
    label: 'Light Personalization',
    description: 'Minor adjustments to match your background',
    icon: '✨'
  },
  {
    value: 'moderate',
    label: 'Moderate Personalization',
    description: 'Balanced adaptation with examples from your experience',
    icon: '🎯'
  },
  {
    value: 'deep',
    label: 'Deep Personalization',
    description: 'Comprehensive rewrite tailored to your expertise level',
    icon: '🚀'
  }
];

export default function PersonalizeModal({ isOpen, onClose, onConfirm, currentLevel = 'moderate' }: PersonalizeModalProps) {
  const [selectedLevel, setSelectedLevel] = useState(currentLevel);

  // Reset selected level when modal opens
  useEffect(() => {
    if (isOpen) {
      setSelectedLevel(currentLevel);
    }
  }, [isOpen, currentLevel]);

  if (!isOpen) return null;

  const handleConfirm = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    e?.preventDefault();
    onConfirm(selectedLevel);
    onClose();
  };

  const handleOptionClick = (level: string, e?: React.MouseEvent) => {
    e?.stopPropagation();
    e?.preventDefault();
    if (selectedLevel !== level) {
      setSelectedLevel(level);
    }
  };

  const handleCancel = (e?: React.MouseEvent) => {
    e?.stopPropagation();
    e?.preventDefault();
    onClose();
  };

  return (
    <div className={styles.overlay} onClick={handleCancel}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <div className={styles.header}>
          <h2>Personalize Content</h2>
          <button className={styles.closeButton} onClick={handleCancel} type="button">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>
        </div>
        
        <div className={styles.content}>
          <p className={styles.description}>
            Choose how much you want the content to be personalized based on your background:
          </p>
          
          <div className={styles.options}>
            {personalizationLevels.map((level) => (
              <div
                key={level.value}
                className={`${styles.option} ${selectedLevel === level.value ? styles.selected : ''}`}
                onClick={(e) => handleOptionClick(level.value, e)}
                role="button"
                tabIndex={0}
                aria-selected={selectedLevel === level.value}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    e.stopPropagation();
                    handleOptionClick(level.value, e as any);
                  }
                }}
              >
                <div className={styles.optionIcon}>{level.icon}</div>
                <div className={styles.optionContent}>
                  <h3>{level.label}</h3>
                  <p>{level.description}</p>
                </div>
                <div className={styles.radio}>
                  {selectedLevel === level.value ? <div className={styles.radioDot}></div> : null}
                </div>
              </div>
            ))}
          </div>
        </div>
        
        <div className={styles.footer}>
          <button className={styles.cancelButton} onClick={handleCancel} type="button">
            Cancel
          </button>
          <button className={styles.confirmButton} onClick={handleConfirm} type="button">
            Personalize
          </button>
        </div>
      </div>
    </div>
  );
}

