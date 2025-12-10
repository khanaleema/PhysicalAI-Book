import useDocusaurusContext from '@docusaurus/useDocusaurusContext';

/**
 * Get the API URL from configuration or environment
 * Priority:
 * 1. window.CHATBOT_API_URL (injected at runtime)
 * 2. siteConfig.customFields.apiUrl (set in docusaurus.config.ts)
 * 3. Default to Hugging Face Space URL
 */
export function getApiUrl(): string {
  if (typeof window !== 'undefined') {
    // Check if injected via script tag
    const injectedUrl = (window as any).CHATBOT_API_URL;
    if (injectedUrl) return injectedUrl;
  }
  
  // For server-side rendering, we need to use the config
  // This will be available in client-side components via useDocusaurusContext
  return 'https://aleemakhan-ai-book-be.hf.space';
}

/**
 * Hook to get API URL in React components
 */
export function useApiUrl(): string {
  const {siteConfig} = useDocusaurusContext();
  
  if (typeof window !== 'undefined') {
    const injectedUrl = (window as any).CHATBOT_API_URL;
    if (injectedUrl) return injectedUrl;
  }
  
  const configUrl = (siteConfig.customFields as any)?.apiUrl;
  if (configUrl) return configUrl;
  
  return 'https://aleemakhan-ai-book-be.hf.space';
}

