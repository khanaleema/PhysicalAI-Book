import React from 'react';
import NavbarActionsWrapper from '@site/src/components/NavbarActionsWrapper';
import ChapterPersonalizeWrapper from '@site/src/components/ChapterPersonalizeWrapper';
import Chatbot from '@site/src/components/Chatbot';
import { useApiUrl } from '@site/src/lib/api';

// Default implementation, that you can customize
export default function Root({children}: {children: React.ReactNode}) {
  const apiUrl = useApiUrl();

  return (
    <>
      {children}
      <NavbarActionsWrapper />
      <ChapterPersonalizeWrapper />
      <Chatbot apiUrl={apiUrl} />
    </>
  );
}

