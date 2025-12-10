import { useEffect } from 'react';
import { useHistory } from '@docusaurus/router';

export default function SignInAPI() {
  const history = useHistory();
  
  useEffect(() => {
    // This is a client-side redirect
    history.push('/auth/signin');
  }, [history]);
  
  return null;
}

