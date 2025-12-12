import React from 'react';
import PersonalizeButton from '../PersonalizeButton';

interface ChapterActionsProps {
  chapterPath: string;
  content: string;
}

export default function ChapterActions({ chapterPath, content }: ChapterActionsProps) {
  return (
    <div style={{ marginBottom: '24px' }}>
      <PersonalizeButton
        chapterPath={chapterPath}
        content={content}
        onPersonalize={(personalizedContent) => {
          localStorage.setItem(`personalized_${chapterPath}`, personalizedContent);
          window.location.reload();
        }}
      />
    </div>
  );
}

