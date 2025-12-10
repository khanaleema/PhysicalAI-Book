import React from 'react';
import PersonalizeButton from '../PersonalizeButton';
import TranslateButton from '../TranslateButton';

interface ChapterActionsProps {
  chapterPath: string;
  content: string;
}

export default function ChapterActions({ chapterPath, content }: ChapterActionsProps) {
  return (
    <div style={{ 
      display: 'flex', 
      flexDirection: 'column', 
      gap: '1rem',
      marginTop: '2rem',
      marginBottom: '2rem'
    }}>
      <PersonalizeButton chapterPath={chapterPath} originalContent={content} />
      <TranslateButton chapterPath={chapterPath} originalContent={content} />
    </div>
  );
}

