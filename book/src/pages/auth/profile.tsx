import React, { useState, useEffect } from 'react';
import Layout from '@theme/Layout';
import { useHistory } from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';
import { useApiUrl } from '@site/src/lib/api';
import styles from './auth.module.css';

interface BackgroundInfo {
  softwareExperience: string;
  hardwareExperience: string;
  programmingLanguages: string[];
  roboticsExperience: string;
  educationLevel: string;
}

export default function Profile() {
  const [user, setUser] = useState<any>(null);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
  });
  const [background, setBackground] = useState<BackgroundInfo>({
    softwareExperience: '',
    hardwareExperience: '',
    programmingLanguages: [],
    roboticsExperience: '',
    educationLevel: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const history = useHistory();
  const baseUrl = useBaseUrl('/');
  const apiUrl = useApiUrl();

  const programmingLanguagesOptions = [
    'Python', 'C++', 'JavaScript/TypeScript', 'Java', 'ROS 2', 
    'MATLAB', 'Rust', 'Go', 'Other'
  ];

  useEffect(() => {
    const userStr = localStorage.getItem('user');
    const backgroundStr = localStorage.getItem('userBackground');
    
    if (userStr) {
      const userData = JSON.parse(userStr);
      setUser(userData);
      setFormData({
        name: userData.name || '',
        email: userData.email || '',
      });
    }
    
    if (backgroundStr) {
      setBackground(JSON.parse(backgroundStr));
    }
    
    if (!userStr) {
      history.push('/auth/signin');
    }
  }, [history]);

  const handleBackgroundChange = (field: keyof BackgroundInfo, value: string | string[]) => {
    setBackground(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      // Check for token in both possible keys (authToken or token)
      let token = localStorage.getItem('authToken') || localStorage.getItem('token');
      if (!token) {
        // If no token, try to get from user object
        const userStr = localStorage.getItem('user');
        if (userStr) {
          const userData = JSON.parse(userStr);
          // If user exists but no token, fallback to localStorage update only
          console.log('⚠️ No token found, updating localStorage only');
          const updatedUser = {
            ...user,
            name: formData.name,
            background: background
          };
          
          localStorage.setItem('user', JSON.stringify(updatedUser));
          localStorage.setItem('userBackground', JSON.stringify(background));
          
          setUser(updatedUser);
          setSuccess('Profile updated successfully! (Saved locally)');
          
          setTimeout(() => {
            setSuccess('');
            window.location.href = 'https://khanaleema.github.io/PhysicalAI-Book/docs/preface/';
          }, 1500);
          return;
        }
        
        setError('Authentication required. Please sign in again.');
        setTimeout(() => {
          history.push('/auth/signin');
        }, 2000);
        return;
      }

      // Call API to update profile
      const response = await fetch(`${apiUrl}/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: formData.name,
          background: background
        })
      });

      if (!response.ok) {
        // If 503 or database error, fallback to localStorage only
        if (response.status === 503 || response.status === 500) {
          console.log('⚠️ Database unavailable, updating localStorage only');
          // Update localStorage directly
          const updatedUser = {
            ...user,
            name: formData.name,
            background: background
          };
          
          localStorage.setItem('user', JSON.stringify(updatedUser));
          localStorage.setItem('userBackground', JSON.stringify(background));
          
          setUser(updatedUser);
          setSuccess('Profile updated successfully! (Saved locally)');
          
          setTimeout(() => {
            setSuccess('');
            // Navigate to docs/preface - use full URL
            window.location.href = 'https://khanaleema.github.io/PhysicalAI-Book/docs/preface/';
          }, 1500);
          return;
        }
        
        const errorData = await response.json().catch(() => ({ detail: 'Failed to update profile' }));
        throw new Error(errorData.detail || 'Failed to update profile');
      }

      const updatedUserData = await response.json();
      
      // Update localStorage with new data
      const updatedUser = {
        ...user,
        name: updatedUserData.name || formData.name,
        background: updatedUserData.background || background
      };
      
      localStorage.setItem('user', JSON.stringify(updatedUser));
      localStorage.setItem('userBackground', JSON.stringify(updatedUserData.background || background));
      
      setUser(updatedUser);
      setSuccess('Profile updated successfully!');
      
      setTimeout(() => {
        setSuccess('');
        // Navigate to docs/preface - use full URL
        window.location.href = 'https://khanaleema.github.io/PhysicalAI-Book/docs/preface/';
      }, 1500);
    } catch (err: any) {
      setError(err.message || 'Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

  return (
    <Layout title="Profile Settings">
      <div className={styles.settingsContainer}>
        <div className={styles.settingsCard}>
          <div className={styles.settingsHeader}>
            <div className={styles.headerContent}>
              <h1>Edit Profile</h1>
              <p className={styles.settingsSubtitle}>Update your account information and learning preferences</p>
            </div>
            <div className={styles.avatarLarge}>
              {user.name?.charAt(0).toUpperCase() || 'U'}
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className={styles.settingsForm}>
            <div className={styles.settingsSection}>
              <h2 className={styles.sectionTitle}>Account Information</h2>
            <div className={styles.formGroup}>
              <label>Full Name</label>
              <input
                type="text"
                value={formData.name}
                onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                required
                disabled={loading}
              />
            </div>
            
            <div className={styles.formGroup}>
              <label>Email</label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData(prev => ({ ...prev, email: e.target.value }))}
                required
                disabled={loading}
              />
            </div>

            </div>

            <div className={styles.settingsSection}>
              <h2 className={styles.sectionTitle}>Learning Background</h2>
              <p className={styles.sectionDescription}>Update your background to improve content personalization</p>

            <div className={styles.formGroup}>
              <label>Software Development Experience</label>
              <select
                value={background.softwareExperience}
                onChange={(e) => handleBackgroundChange('softwareExperience', e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select...</option>
                <option value="beginner">Beginner (0-1 years)</option>
                <option value="intermediate">Intermediate (1-3 years)</option>
                <option value="advanced">Advanced (3-5 years)</option>
                <option value="expert">Expert (5+ years)</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Hardware/Robotics Experience</label>
              <select
                value={background.hardwareExperience}
                onChange={(e) => handleBackgroundChange('hardwareExperience', e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select...</option>
                <option value="none">None</option>
                <option value="basic">Basic (Arduino/Raspberry Pi)</option>
                <option value="intermediate">Intermediate (ROS, sensors)</option>
                <option value="advanced">Advanced (Humanoid robots, advanced control)</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Programming Languages (Select all that apply)</label>
              <div className={styles.checkboxGroup}>
                {programmingLanguagesOptions.map(lang => (
                  <label key={lang} className={styles.checkbox}>
                    <input
                      type="checkbox"
                      checked={background.programmingLanguages.includes(lang)}
                      onChange={(e) => {
                        const current = background.programmingLanguages;
                        if (e.target.checked) {
                          handleBackgroundChange('programmingLanguages', [...current, lang]);
                        } else {
                          handleBackgroundChange('programmingLanguages', current.filter(l => l !== lang));
                        }
                      }}
                      disabled={loading}
                    />
                    <span>{lang}</span>
                  </label>
                ))}
              </div>
            </div>

            <div className={styles.formGroup}>
              <label>Robotics Experience Level</label>
              <select
                value={background.roboticsExperience}
                onChange={(e) => handleBackgroundChange('roboticsExperience', e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select...</option>
                <option value="none">No experience</option>
                <option value="academic">Academic/Research</option>
                <option value="hobby">Hobby projects</option>
                <option value="professional">Professional</option>
              </select>
            </div>

            <div className={styles.formGroup}>
              <label>Education Level</label>
              <select
                value={background.educationLevel}
                onChange={(e) => handleBackgroundChange('educationLevel', e.target.value)}
                required
                disabled={loading}
              >
                <option value="">Select...</option>
                <option value="high-school">High School</option>
                <option value="bachelor">Bachelor's Degree</option>
                <option value="master">Master's Degree</option>
                <option value="phd">PhD</option>
                <option value="professional">Professional/Industry</option>
              </select>
            </div>

            </div>

            {error && <div className={styles.error}>{error}</div>}
            {success && <div className={styles.success}>{success}</div>}
            
            <div className={styles.settingsFooter}>
              <button 
                type="button" 
                onClick={() => window.location.href = 'https://khanaleema.github.io/PhysicalAI-Book/docs/preface/'} 
                className={styles.cancelButton}
                disabled={loading}
              >
                Cancel
              </button>
              <button type="submit" disabled={loading} className={styles.submitButton}>
                {loading ? 'Saving...' : 'Save Changes'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Layout>
  );
}

