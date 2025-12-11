import React, { useState, useEffect } from 'react';
import Link from '@docusaurus/Link';
import useBaseUrl from '@docusaurus/useBaseUrl';
import LanguageSwitcher from '@site/src/components/LanguageSwitcher';
import styles from './styles.module.css';

export default function NavbarActions() {
  const baseUrl = useBaseUrl('/');
  const [user, setUser] = useState<any>(null);
  const [showMenu, setShowMenu] = useState(false);

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    if (userStr) {
      setUser(JSON.parse(userStr));
    }
    
    // Close dropdown on outside click
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (showMenu && !target.closest(`.${styles.userMenuContainer}`)) {
        setShowMenu(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showMenu]);

  const handleSignOut = () => {
    localStorage.removeItem('user');
    localStorage.removeItem('userBackground');
    localStorage.removeItem('authToken');
    setUser(null);
    setShowMenu(false);
    window.location.href = baseUrl;
  };

  return (
    <div className={styles.navbarActions}>
      {/* Language Switcher */}
      <LanguageSwitcher />
      
      {/* User Menu */}
      {!user ? (
        <>
          <Link to="/auth/signin" className={styles.signInButton}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"></path>
              <polyline points="10 17 15 12 10 7"></polyline>
              <line x1="15" y1="12" x2="3" y2="12"></line>
            </svg>
            <span>Sign In</span>
          </Link>
          <Link to="/auth/signup" className={styles.signUpButton}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
              <circle cx="8.5" cy="7" r="4"></circle>
              <line x1="20" y1="8" x2="20" y2="14"></line>
              <line x1="23" y1="11" x2="17" y2="11"></line>
            </svg>
            <span>Sign Up</span>
          </Link>
        </>
      ) : (
        <div className={styles.userMenuContainer}>
          <button 
            className={styles.userInfo} 
            onClick={() => setShowMenu(!showMenu)}
            aria-label="User menu"
          >
            <div className={styles.avatar}>
              {user.name?.charAt(0).toUpperCase() || 'U'}
            </div>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </button>
          {showMenu && (
            <>
              <div className={styles.dropdownOverlay} onClick={() => setShowMenu(false)}></div>
              <div className={styles.dropdown}>
                <div className={styles.dropdownHeader}>
                  <div className={styles.dropdownAvatar}>
                    {user.name?.charAt(0).toUpperCase() || 'U'}
                  </div>
                  <div>
                    <strong>{user.name}</strong>
                    <div className={styles.email}>{user.email}</div>
                  </div>
                </div>
                <div className={styles.divider}></div>
                <Link to={`${baseUrl}auth/profile/`} className={styles.dropdownItem} onClick={() => setShowMenu(false)}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                  </svg>
                  <span>Edit Profile</span>
                </Link>
                <div className={styles.divider}></div>
                <div className={styles.dropdownItem} onClick={handleSignOut}>
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                    <polyline points="16 17 21 12 16 7"></polyline>
                    <line x1="21" y1="12" x2="9" y2="12"></line>
                  </svg>
                  <span>Sign Out</span>
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
}
