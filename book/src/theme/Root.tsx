import React from 'react';
import NavbarActionsWrapper from '@site/src/components/NavbarActionsWrapper';
import Chatbot from '@site/src/components/Chatbot';
import ChapterPersonalize from '@site/src/components/ChapterPersonalize';
import { useApiUrl } from '@site/src/lib/api';
import '@site/src/lib/i18n'; // Initialize i18n

// Default implementation, that you can customize
export default function Root({children}: {children: React.ReactNode}) {
  const apiUrl = useApiUrl();

  return (
    <>
      {children}
      <NavbarActionsWrapper />
      <Chatbot apiUrl={apiUrl} />
      <ChapterPersonalize />
    </>
  );
}

