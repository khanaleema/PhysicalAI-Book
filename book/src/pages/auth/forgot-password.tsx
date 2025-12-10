import React, { useState } from 'react';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import { useHistory } from '@docusaurus/router';
import styles from './auth.module.css';
import { useApiUrl } from '@site/src/lib/api';

export default function ForgotPassword() {
  const apiUrl = useApiUrl();
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1); // 1: request reset, 2: reset password
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const history = useHistory();

  const handleRequestReset = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    try {
      const response = await fetch(`${apiUrl}/auth/forgot-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });

      const data = await response.json();
      
      if (response.ok) {
        if (data.resetToken) {
          setSuccess('Password reset token generated! Use it below to reset your password.');
          setResetToken(data.resetToken);
          setStep(2);
        } else if (data.error === 'Email not registered') {
          setError('This email is not registered. Please sign up first or check your email address.');
        } else {
          setSuccess(data.message || 'Password reset link sent! Please check your email.');
        }
      } else {
        setError(data.detail || 'Failed to send reset link');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }

    setLoading(true);

    try {
      const response = await fetch(`${apiUrl}/auth/reset-password`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          resetToken,
          newPassword,
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        setSuccess('Password reset successfully! Redirecting to sign in...');
        setTimeout(() => {
          history.push('/auth/signin');
        }, 2000);
      } else {
        setError(data.detail || 'Failed to reset password');
      }
    } catch (err) {
      setError('Network error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Layout title="Forgot Password">
      <div className={styles.authContainer}>
        <div className={styles.authCard}>
          <h1>{step === 1 ? 'Forgot Password' : 'Reset Password'}</h1>
          <p style={{ textAlign: 'center', color: '#666', marginBottom: '2rem', fontSize: '0.95rem' }}>
            {step === 1 
              ? 'Enter your email to receive a password reset link'
              : 'Enter your new password'
            }
          </p>

          {step === 1 ? (
            <form onSubmit={handleRequestReset} className={styles.authForm}>
              <div className={styles.formGroup}>
                <label>Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  required
                  disabled={loading}
                  placeholder="Enter your email address"
                />
              </div>
              {error && <div className={styles.error}>{error}</div>}
              {success && <div className={styles.success}>{success}</div>}
              {resetToken && (
                <div className={styles.tokenInfo}>
                  <p><strong>📧 Demo Reset Token (for testing):</strong></p>
                  <code style={{ 
                    display: 'block', 
                    padding: '0.75rem', 
                    background: '#f5f5f5', 
                    borderRadius: '6px',
                    marginTop: '0.5rem',
                    wordBreak: 'break-all',
                    fontSize: '0.9rem',
                    border: '1px solid #e0e0e0'
                  }}>
                    {resetToken}
                  </code>
                  <p style={{ fontSize: '0.85rem', color: '#666', marginTop: '0.75rem', marginBottom: 0 }}>
                    ⚠️ In production, this token would be sent to your email. Copy it and use it in the next step.
                  </p>
                </div>
              )}
              <button type="submit" disabled={loading} className={styles.submitButton}>
                {loading ? 'Sending...' : 'Send Reset Link'}
              </button>
              <p className={styles.switchAuth}>
                Remember your password? <Link to="/auth/signin">Sign in</Link>
              </p>
            </form>
          ) : (
            <form onSubmit={handleResetPassword} className={styles.authForm}>
              <div className={styles.formGroup}>
                <label>Reset Token</label>
                <input
                  type="text"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  required
                  disabled={loading}
                  placeholder="Enter the reset token from email"
                />
              </div>
              <div className={styles.formGroup}>
                <label>New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                  disabled={loading}
                  minLength={8}
                  placeholder="Enter new password (min 8 characters)"
                />
              </div>
              <div className={styles.formGroup}>
                <label>Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  disabled={loading}
                  minLength={8}
                  placeholder="Confirm new password"
                />
              </div>
              {error && <div className={styles.error}>{error}</div>}
              {success && <div className={styles.success}>{success}</div>}
              <button type="submit" disabled={loading} className={styles.submitButton}>
                {loading ? 'Resetting...' : 'Reset Password'}
              </button>
              <button
                type="button"
                onClick={() => setStep(1)}
                className={styles.backButton}
                disabled={loading}
              >
                ← Back
              </button>
            </form>
          )}
        </div>
      </div>
    </Layout>
  );
}

