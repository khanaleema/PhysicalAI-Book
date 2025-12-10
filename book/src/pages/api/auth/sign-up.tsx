import { useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

export default function SignUpAPI() {
  const history = useHistory();
  
  useEffect(() => {
    // This is a client-side redirect
    history.push('/auth/signup');
  }, [history]);
  
  return null;
}

