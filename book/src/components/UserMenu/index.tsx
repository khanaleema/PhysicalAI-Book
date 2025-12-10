import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

export default function UserMenu() {
  const baseUrl = useBaseUrl('/');
  const [user, setUser] = useState<any>(null);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
  }, []);

  const handleSignOut = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('userBackground');
    localStorage.removeItem('authToken');
    setUser(null);
    setShowMenu(false);
    // Redirect to home page with baseUrl
    window.location.href = baseUrl;
  };

  if (!user) {
    return (
      <div className={styles.userMenu}>
        <Link to="/auth/signin" className={styles.signInButton}>
          Sign In
        </Link>
        <Link to="/auth/signup" className={styles.signUpButton}>
          Sign Up
        </Link>
      </div>
    );
  }

  return (
    <div className={styles.userMenu}>
      <div className={styles.userInfo} onClick={() => setShowMenu(!showMenu)}>
        <div className={styles.avatar}>
          {user.name?.charAt(0).toUpperCase() || 'U'}
        </div>
        <span className={styles.userName}>{user.name}</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <polyline points="6 9 12 15 18 9"></polyline>
        </svg>
      </div>
      {showMenu && (
        <div className={styles.dropdown}>
          <div className={styles.dropdownItem}>
            <strong>{user.name}</strong>
            <div className={styles.email}>{user.email}</div>
          </div>
          <div className={styles.divider}></div>
          <div className={styles.dropdownItem} onClick={handleSignOut}>
            Sign Out
          </div>
        </div>
      )}
    </div>
  );
}

