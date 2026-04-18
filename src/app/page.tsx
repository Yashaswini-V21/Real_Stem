import { LessonGenerator } from '@/components/lesson-generator';

const highlights = [
  {
    title: 'Daily news scanning',
    description:
      'Collects STEM-relevant stories from trusted news sources and clusters them by topic, age level, and geography.',
  },
  {
    title: 'Teacher-controlled generation',
    description:
      'Draft lesson plans, activities, and discussion prompts automatically, then review and edit before sharing.',
  },
  {
    title: 'Localized relevance',
    description:
      'Surface Indian, US, or region-specific examples so students see their own world reflected in the lesson.',
  },
];

const workflow = [
  'News ingestion and topic detection',
  'STEM relevance scoring and grade matching',
  'Standards-aware lesson generation',
  'Teacher review, edit, and publish',
];

const subjects = ['Physics', 'Chemistry', 'Biology', 'Mathematics', 'Computer Science', 'Earth Science'];

export default function Home() {
  return (
    <main className="page-shell">
      <section className="hero-card">
        <div className="hero-copy">
          <p className="eyebrow">RealSTEM</p>
          <h1>Turn breaking news into STEM lessons students actually care about.</h1>
          <p className="lede">
            Every day, RealSTEM scans current events, filters for real-world STEM relevance,
            and drafts standards-aligned lessons that teachers can review in minutes instead of hours.
          </p>
          <div className="hero-actions">
            <a className="primary-action" href="#workflow">See the workflow</a>
            <a className="secondary-action" href="#prototype">View the prototype brief</a>
          </div>
        </div>

        <aside className="news-panel" id="prototype">
          <div className="panel-header">
            <span>Today&apos;s example</span>
            <span className="status-pill">AI drafted</span>
          </div>
          <h2>Tesla recalls 2M cars after autopilot issue</h2>
          <p>
            Suggested lesson: machine learning safety, edge cases, probability, and protocol design
            for high school physics or computer science.
          </p>
          <ol>
            <li>How does autopilot work?</li>
            <li>What went wrong in the edge cases?</li>
            <li>Is 99.9% accuracy enough for safety?</li>
            <li>Design a testing protocol for the model.</li>
          </ol>
        </aside>
      </section>

      <section className="stats-grid">
        <div className="stat-card">
          <span className="stat-value">Daily</span>
          <span className="stat-label">fresh lesson opportunities from the news</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">Multi-subject</span>
          <span className="stat-label">physics, math, biology, chemistry, and CS</span>
        </div>
        <div className="stat-card">
          <span className="stat-value">Teacher-first</span>
          <span className="stat-label">review, edit, and save favorite lessons</span>
        </div>
      </section>

      <section className="content-grid" aria-labelledby="problem-title">
        <div className="section-intro">
          <p className="eyebrow">The problem</p>
          <h2 id="problem-title">STEM feels abstract when examples stop at the textbook.</h2>
        </div>
        <div className="problem-card">
          <p>
            RealSTEM closes the gap between classroom concepts and the world students already see in the news,
            their community, and their daily lives.
          </p>
          <p>
            The result is a lesson engine that makes “When will I use this?” easier to answer with something concrete,
            timely, and local.
          </p>
        </div>
      </section>

      <section className="feature-grid">
        {highlights.map((item) => (
          <article className="feature-card" key={item.title}>
            <h3>{item.title}</h3>
            <p>{item.description}</p>
          </article>
        ))}
      </section>

      <LessonGenerator />

      <section className="workflow-section" id="workflow">
        <div className="section-intro">
          <p className="eyebrow">How it works</p>
          <h2>A simple pipeline from news to lesson plan.</h2>
        </div>
        <div className="workflow-list">
          {workflow.map((step, index) => (
            <div className="workflow-step" key={step}>
              <span className="step-index">0{index + 1}</span>
              <p>{step}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="bottom-grid">
        <article className="tone-card">
          <p className="eyebrow">Subject coverage</p>
          <div className="chip-row">
            {subjects.map((subject) => (
              <span className="chip" key={subject}>{subject}</span>
            ))}
          </div>
        </article>

        <article className="tone-card accent-card">
          <p className="eyebrow">MVP scope</p>
          <ul>
            <li>News ingestion from APIs and feeds</li>
            <li>STEM classification and grade-level ranking</li>
            <li>Lesson generation with teacher review</li>
            <li>Saved lessons and engagement analytics</li>
          </ul>
        </article>
      </section>
    </main>
  );
}