import React from 'react';
import styles from './styles.module.css';

interface PersonalizeModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectLevel: (level: string) => void;
  currentLevel: string | null;
}

const LEVELS = [
  {
    id: 'beginner',
    name: 'Beginner',
    description: 'New to Physical AI and Robotics. Prefer simpler explanations with basic concepts.',
    icon: '🌱',
    color: '#10b981',
  },
  {
    id: 'intermediate',
    name: 'Intermediate',
    description: 'Have some background knowledge. Prefer balanced explanations with practical examples.',
    icon: '🚀',
    color: '#3b82f6',
  },
  {
    id: 'advanced',
    name: 'Advanced',
    description: 'Experienced professional. Prefer detailed technical content with advanced concepts.',
    icon: '⚡',
    color: '#8b5cf6',
  },
];

export default function PersonalizeModal({
  isOpen,
  onClose,
  onSelectLevel,
  currentLevel,
}: PersonalizeModalProps) {
  if (!isOpen) return null;

  return (
    <div className={styles.modalOverlay} onClick={onClose}>
      <div className={styles.modalContent} onClick={(e) => e.stopPropagation()}>
        <div className={styles.modalHeader}>
          <h2 className={styles.modalTitle}>Personalize Your Learning</h2>
          <button className={styles.closeButton} onClick={onClose}>
            ×
          </button>
        </div>
        
        <p className={styles.modalDescription}>
          Select your experience level to get content personalized to your needs.
          You can change this anytime.
        </p>

        <div className={styles.levelsContainer}>
          {LEVELS.map((level) => (
            <button
              key={level.id}
              className={`${styles.levelCard} ${
                currentLevel === level.id ? styles.levelCardActive : ''
              }`}
              onClick={() => onSelectLevel(level.id)}
              style={{
                borderColor: currentLevel === level.id ? level.color : '#e5e7eb',
              }}
            >
              <div className={styles.levelIcon} style={{ color: level.color }}>
                {level.icon}
              </div>
              <div className={styles.levelInfo}>
                <h3 className={styles.levelName}>{level.name}</h3>
                <p className={styles.levelDescription}>{level.description}</p>
              </div>
              {currentLevel === level.id && (
                <div className={styles.checkmark} style={{ color: level.color }}>
                  ✓
                </div>
              )}
            </button>
          ))}
        </div>

        <div className={styles.modalFooter}>
          <button className={styles.cancelButton} onClick={onClose}>
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}

