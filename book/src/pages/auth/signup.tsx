import React, { useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useHistory } from '@docusaurus/router';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './auth.module.css';
import { useApiUrl } from '@site/src/lib/api';

interface BackgroundInfo {
  softwareExperience: string;
  hardwareExperience: string;
  programmingLanguages: string[];
  roboticsExperience: string;
  educationLevel: string;
}

export default function SignUp() {
  const apiUrl = useApiUrl();
  const baseUrl = useBaseUrl('/');
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [background, setBackground] = useState<BackgroundInfo>({
    softwareExperience: '',
    hardwareExperience: '',
    programmingLanguages: [],
    roboticsExperience: '',
    educationLevel: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const history = useHistory();

  const programmingLanguagesOptions = [
    'Python', 'C++', 'JavaScript/TypeScript', 'Java', 'ROS 2', 
    'MATLAB', 'Rust', 'Go', 'Other'
  ];

  const handleBackgroundChange = (field: keyof BackgroundInfo, value: string | string[]) => {
    setBackground(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (step === 1) {
      if (formData.password !== formData.confirmPassword) {
        setError('Passwords do not match');
        return;
      }
      if (formData.password.length < 8) {
        setError('Password must be at least 8 characters');
        return;
      }
      setStep(2);
      return;
    }

    // Step 2: Submit signup with background info
    setLoading(true);
    try {
      const response = await fetch(`${apiUrl}/auth/sign-up`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: formData.name,
          email: formData.email,
          password: formData.password,
          background,
        }),
      });

      const data = await response.json();

      if (response.ok) {
        // Auto sign-in after successful signup
        localStorage.setItem('user', JSON.stringify(data.user));
        localStorage.setItem('userBackground', JSON.stringify(background));
        localStorage.setItem('authToken', data.token);
        
        // Show success message
        alert('Account created successfully! You are now signed in.');
        
        // Redirect to textbook (preface page) with baseUrl
        const prefacePath = `${baseUrl}docs/preface/`;
        window.location.href = prefacePath;
      } else {
        setError(data.detail || 'Sign up failed');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Sign Up">
      <div className={styles.authContainer}>
        <div className={styles.authCard}>
          <h1>Create Your Account</h1>
          <p style={{ textAlign: 'center', color: '#666', marginBottom: '2rem', fontSize: '0.95rem' }}>
            Join us to personalize your learning experience
          </p>
          <div className={styles.progressBar}>
            <div className={styles.progressStep} data-active={step >= 1}>
              <span>1</span>
              <label>Account</label>
            </div>
            <div className={styles.progressStep} data-active={step >= 2}>
              <span>2</span>
              <label>Background</label>
            </div>
          </div>

          <form onSubmit={handleSubmit} className={styles.authForm}>
            {step === 1 ? (
              <>
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
                <div className={styles.formGroup}>
                  <label>Password</label>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData(prev => ({ ...prev, password: e.target.value }))}
                    required
                    disabled={loading}
                    minLength={8}
                  />
                </div>
                <div className={styles.formGroup}>
                  <label>Confirm Password</label>
                  <input
                    type="password"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData(prev => ({ ...prev, confirmPassword: e.target.value }))}
                    required
                    disabled={loading}
                  />
                </div>
              </>
            ) : (
              <>
                <h2>Tell us about your background</h2>
                <p className={styles.subtitle}>This helps us personalize your learning experience</p>

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

                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className={styles.backButton}
                  disabled={loading}
                >
                  ← Back
                </button>
              </>
            )}

            {error && <div className={styles.error}>{error}</div>}
            <button type="submit" disabled={loading} className={styles.submitButton}>
              {loading ? 'Processing...' : step === 1 ? 'Continue →' : 'Create Account'}
            </button>
            {step === 1 && (
              <p className={styles.switchAuth}>
                Already have an account? <Link to="/auth/signin">Sign in</Link>
              </p>
            )}
          </form>
        </div>
      </div>
    </Layout>
  );
}

