import type {ReactNode} from 'react';
import clsx from 'clsx';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import {useColorMode} from '@docusaurus/theme-common';
import Footer from '@site/src/components/Footer';

import styles from './index.module.css';

function HomepageHeader() {
  const {siteConfig} = useDocusaurusContext();
  const {isDarkTheme} = useColorMode();
  const heroImageUrl = useBaseUrl('/img/hero.svg');
  
  return (
    <header className={clsx(styles.heroSection, isDarkTheme && styles.heroSectionDark)}>
      <div className="container">
        <div className={styles.heroContent}>
          <div className={styles.heroText}>
            <div className={styles.badges}>
              <span className={styles.badge}>✨ Open Source</span>
              <span className={styles.badge}>🤖 Physical AI</span>
              <span className={styles.badge}>🎯 Comprehensive</span>
            </div>
            <Heading as="h1" className={styles.heroTitle}>
              {siteConfig.title}
            </Heading>
            <p className={styles.heroSubtitle}>
              A Comprehensive Guide to Embodied Intelligence and Humanoid Systems
            </p>
            <div className={styles.heroAuthor}>
              <span className={styles.authorLabel}>By</span>
              <span className={styles.authorName}>Aleema Khan</span>
            </div>
            <p className={styles.heroDescription}>
              Master the complete journey from foundational robotics concepts to cutting-edge 
              research in Physical AI and Humanoid Robotics. Build intelligent systems that
              perceive, reason, and act in the physical world..!!
            </p>
            <div className={styles.heroButtons}>
              <Link
                className="button button--primary button--lg"
                to="/docs/preface">
                📖 Start Reading →
              </Link>
              <a
                className="button button--secondary button--lg"
                href="https://github.com/khanaleema/"
                target="_blank"
                rel="noopener noreferrer">
                <svg className={styles.githubIcon} viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
                View on GitHub
              </a>
            </div>
          </div>
          <div className={styles.heroVisual}>
            <div className={styles.heroImageContainer}>
              <img 
                src={heroImageUrl} 
                alt="Physical AI & Humanoid Robotics" 
                className={styles.heroImage}
              />
            </div>
          </div>
        </div>
      </div>
    </header>
  );
}

function LearningSpectrum() {
  const {isDarkTheme} = useColorMode();
  
  return (
    <section className={clsx(styles.spectrumSection, isDarkTheme && styles.spectrumSectionDark)}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2" className={styles.sectionTitle}>
            Understanding Physical AI
          </Heading>
          <p className={styles.sectionSubtitle}>
            Three levels of embodied intelligence. This book takes you from foundations to advanced research.
          </p>
        </div>
        
        <div className={styles.spectrumGrid}>
          <div className={styles.spectrumCard}>
            <div className={styles.spectrumIcon}>🔧</div>
            <Heading as="h3" className={styles.spectrumTitle}>
              Foundations
            </Heading>
            <p className={styles.spectrumSubtitle}>AI as Helper</p>
            <p className={styles.spectrumDescription}>
              Master robotics fundamentals: kinematics, dynamics, sensors, and control systems. 
              Build the mathematical and engineering foundation for intelligent robots.
            </p>
            <ul className={styles.spectrumList}>
              <li>Robot kinematics & dynamics</li>
              <li>Sensor integration & perception</li>
              <li>Control systems & actuation</li>
            </ul>
            <p className={styles.spectrumExample}>
              <strong>Example:</strong> Building a robot arm with precise position control
            </p>
          </div>

          <div className={clsx(styles.spectrumCard, styles.spectrumCardHighlight)}>
            <div className={styles.spectrumBadge}>Focus of This Book</div>
            <div className={styles.spectrumIcon}>🤖</div>
            <Heading as="h3" className={styles.spectrumTitle}>
              Intelligent Systems
            </Heading>
            <p className={styles.spectrumSubtitle}>AI as Co-Creator</p>
            <p className={styles.spectrumDescription}>
              Develop learning-based robots using reinforcement learning, simulation, and AI. 
              Create systems that adapt, learn, and improve through experience.
            </p>
            <ul className={styles.spectrumList}>
              <li>Reinforcement learning for robots</li>
              <li>Sim-to-real transfer</li>
              <li>Neural control policies</li>
            </ul>
            <p className={styles.spectrumExample}>
              <strong>Example:</strong> Training a humanoid to walk using RL in simulation
            </p>
          </div>

          <div className={styles.spectrumCard}>
            <div className={styles.spectrumIcon}>🧠</div>
            <Heading as="h3" className={styles.spectrumTitle}>
              Advanced AI
            </Heading>
            <p className={styles.spectrumSubtitle}>AI IS the Robot</p>
            <p className={styles.spectrumDescription}>
              Integrate large language models, vision transformers, and multimodal AI. 
              Build robots that understand natural language and reason about complex tasks.
            </p>
            <ul className={styles.spectrumList}>
              <li>LLM-powered robot reasoning</li>
              <li>Multimodal perception</li>
              <li>Embodied AI agents</li>
            </ul>
            <p className={styles.spectrumExample}>
              <strong>Example:</strong> Humanoid that understands verbal commands and plans actions
            </p>
          </div>
        </div>

        <div className={styles.spectrumProgression}>
          <div className={styles.progressionStep}>
            <div className={styles.progressionNumber}>1</div>
            <div className={styles.progressionLabel}>Foundations</div>
          </div>
          <div className={styles.progressionArrow}>→</div>
          <div className={styles.progressionStep}>
            <div className={styles.progressionNumber}>2</div>
            <div className={styles.progressionLabel}>Intelligent Systems</div>
          </div>
          <div className={styles.progressionArrow}>→</div>
          <div className={styles.progressionStep}>
            <div className={styles.progressionNumber}>3</div>
            <div className={styles.progressionLabel}>Advanced AI</div>
          </div>
        </div>
      </div>
    </section>
  );
}

function CorePillars() {
  const {isDarkTheme} = useColorMode();
  const pillars = [
    {
      icon: '📚',
      title: 'Comprehensive Coverage',
      description: '14 major parts covering everything from foundations to cutting-edge research. 60+ chapters with hands-on examples.',
      highlight: false,
    },
    {
      icon: '🔬',
      title: 'Research-Oriented',
      description: 'Deep dive into state-of-the-art techniques. Learn advanced locomotion, safety-critical control, and transformer-based robot brains.',
      highlight: false,
    },
    {
      icon: '🤖',
      title: 'Practical Applications',
      description: 'Real-world case studies from healthcare, manufacturing, space exploration, and service industries. Build deployable systems.',
      highlight: true,
    },
    {
      icon: '🧪',
      title: 'Simulation & Learning',
      description: 'Master physics engines (MuJoCo, Isaac Gym), reinforcement learning, and sim-to-real transfer for efficient robot development.',
      highlight: false,
    },
    {
      icon: '👥',
      title: 'Human-Robot Interaction',
      description: 'Design safe, intuitive interfaces. Understand social robotics, communication modalities, and trust-building mechanisms.',
      highlight: false,
    },
    {
      icon: '🏗️',
      title: 'Complete Journey',
      description: 'From mathematical foundations to building physical robots. End-to-end understanding of Physical AI systems.',
      highlight: false,
    },
  ];

  return (
    <section className={clsx(styles.pillarsSection, isDarkTheme && styles.pillarsSectionDark)}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2" className={styles.sectionTitle}>
            What Makes This Book Different
          </Heading>
          <p className={styles.sectionSubtitle}>
            A comprehensive, research-focused approach to Physical AI and Humanoid Robotics
          </p>
        </div>

        <div className={styles.pillarsGrid}>
          {pillars.map((pillar, idx) => (
            <div
              key={idx}
              className={clsx(
                styles.pillarCard,
                pillar.highlight && styles.pillarCardHighlight
              )}>
              {pillar.highlight && (
                <div className={styles.pillarBadge}>Most Popular</div>
              )}
              <div className={styles.pillarIcon}>{pillar.icon}</div>
              <Heading as="h3" className={styles.pillarTitle}>
                {pillar.title}
              </Heading>
              <p className={styles.pillarDescription}>{pillar.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function LearningJourney() {
  const {isDarkTheme} = useColorMode();
  const levels = [
    {
      number: '1',
      title: 'Foundations',
      subtitle: 'Building Base',
      description: 'Master robotics mathematics, kinematics, dynamics, and control systems. Understand sensors, actuators, and basic robot behavior.',
      approach: 'Foundations (Mathematical)',
      productivity: 'Core Understanding',
    },
    {
      number: '2',
      title: 'Intelligent Control',
      subtitle: 'Learning Systems',
      description: 'Implement reinforcement learning, neural control policies, and sim-to-real transfer. Build robots that learn and adapt.',
      approach: 'AI-Driven (Learning)',
      productivity: '2-3x Capability',
    },
    {
      number: '3',
      title: 'Advanced Perception',
      subtitle: 'Multimodal AI',
      description: 'Integrate vision transformers, large language models, and multimodal perception. Robots that understand and reason.',
      approach: 'AI-Native (Intelligence)',
      productivity: 'New Capabilities',
      highlight: true,
    },
    {
      number: '4',
      title: 'Real-World Deployment',
      subtitle: 'Physical Systems',
      description: 'Build and deploy physical robots. Hardware design, system integration, and real-world applications across industries.',
      approach: 'Production (Deployment)',
      productivity: 'Industry Ready',
    },
    {
      number: '5',
      title: 'Research Frontier',
      subtitle: 'Cutting-Edge',
      description: 'Explore advanced research: whole-body optimization, safety-critical control, transformer-based robot brains, and future directions.',
      approach: 'Research (Frontier)',
      productivity: 'State-of-the-Art',
    },
  ];

  return (
    <section className={clsx(styles.journeySection, isDarkTheme && styles.journeySectionDark)}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2" className={styles.sectionTitle}>
            Your Learning Journey
          </Heading>
          <p className={styles.sectionSubtitle}>
            Five progressive levels from foundations to research. This book prepares you for levels 1-5.
          </p>
        </div>

        <div className={styles.journeyList}>
          {levels.map((level, idx) => (
            <div
              key={idx}
              className={clsx(
                styles.journeyCard,
                level.highlight && styles.journeyCardHighlight
              )}>
              {level.highlight && (
                <div className={styles.journeyBadge}>BOOK FOCUS</div>
              )}
              <div style={{display: 'flex', gap: '1rem', alignItems: 'flex-start'}}>
                <div className={styles.journeyNumber}>{level.number}</div>
                <div className={styles.journeyContent}>
                  <Heading as="h3" className={styles.journeyTitle}>
                    {level.title}
                  </Heading>
                  <p className={styles.journeySubtitle}>{level.subtitle}</p>
                </div>
              </div>
              <p className={styles.journeyDescription}>{level.description}</p>
              <div className={styles.journeyMeta}>
                <span className={styles.journeyApproach}>
                  <strong>Approach:</strong> {level.approach}
                </span>
                <span className={styles.journeyProductivity}>
                  <strong>Outcome:</strong> {level.productivity}
                </span>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function TheGreatShift() {
  const {isDarkTheme} = useColorMode();
  
  return (
    <section className={clsx(styles.shiftSection, isDarkTheme && styles.shiftSectionDark)}>
      <div className="container">
        <div className={styles.sectionHeader}>
          <Heading as="h2" className={styles.sectionTitle}>
            The Great Shift
          </Heading>
          <p className={styles.sectionSubtitle}>
            From Traditional Robotics to Physical AI
          </p>
        </div>

        <div className={styles.shiftComparison}>
          <div className={styles.shiftColumn}>
            <div className={styles.shiftIcon}>📚</div>
            <Heading as="h3" className={styles.shiftTitle}>
              Traditional Robotics
            </Heading>
            <p className={styles.shiftSubtitle}>The automation era</p>
            <ul className={styles.shiftList}>
              <li>
                <strong>Hand-Coded Control</strong>
                <br />
                Pre-programmed behaviors and trajectories
              </li>
              <li>
                <strong>Rigid Systems</strong>
                <br />
                Fixed responses to known scenarios
              </li>
              <li>
                <strong>Limited Adaptation</strong>
                <br />
                Manual tuning for new environments
              </li>
              <li>
                <strong>Single-Modal Perception</strong>
                <br />
                Basic sensor processing
              </li>
              <li>
                <strong>Engineering-First</strong>
                <br />
                Focus on mechanical design
              </li>
            </ul>
          </div>

          <div className={styles.shiftArrow}>→</div>

          <div className={styles.shiftColumn}>
            <div className={styles.shiftIcon}>🤖</div>
            <Heading as="h3" className={styles.shiftTitle}>
              Physical AI Way
            </Heading>
            <p className={styles.shiftSubtitle}>The intelligence era</p>
            <ul className={styles.shiftList}>
              <li>
                <strong>Learning-Based Control</strong>
                <br />
                Robots that improve through experience
              </li>
              <li>
                <strong>Adaptive Systems</strong>
                <br />
                Generalize to new situations automatically
              </li>
              <li>
                <strong>Continuous Learning</strong>
                <br />
                Self-improving through interaction
              </li>
              <li>
                <strong>Multimodal Intelligence</strong>
                <br />
                Vision, language, and sensor fusion
              </li>
              <li>
                <strong>AI-First Design</strong>
                <br />
                Intelligence as core capability
              </li>
            </ul>
          </div>
        </div>

        <div className={styles.shiftCTA}>
          <Heading as="h3" className={styles.shiftCTATitle}>
            Ready to Build Intelligent Robots?
          </Heading>
          <p className={styles.shiftCTADescription}>
            Join the revolution where robots learn, adapt, and collaborate with humans
          </p>
          <Link
            className="button button--primary button--lg"
            to="/docs/preface">
            Begin Your Journey
          </Link>
        </div>
      </div>
    </section>
  );
}

export default function Home(): ReactNode {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title={`${siteConfig.title} - Comprehensive Textbook`}
      description="A comprehensive, open-source textbook on Physical AI & Humanoid Robotics covering foundational concepts to cutting-edge research">
      <HomepageHeader />
      <main>
        <LearningSpectrum />
        <CorePillars />
        <LearningJourney />
        <TheGreatShift />
      </main>
      <Footer />
    </Layout>
  );
}
