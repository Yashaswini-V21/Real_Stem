'use client';

import { useState, type FormEvent } from 'react';
import type { LessonInput, LessonPlan } from '@/lib/lesson-generator';

const defaultHeadline = 'Tesla recalls 2M cars after autopilot issue';

const exampleHeadlines = [
  'Tesla recalls 2M cars after autopilot issue',
  "India's Chandrayaan-3 lands on the Moon",
  'New city project cuts carbon emissions with smart sensors',
];

export function LessonGenerator() {
  const [headline, setHeadline] = useState(defaultHeadline);
  const [locale, setLocale] = useState<LessonInput['locale']>('India');
  const [gradeLevel, setGradeLevel] = useState<LessonInput['gradeLevel']>('High School');
  const [subject, setSubject] = useState<LessonInput['subject']>('Computer Science');
  const [lesson, setLesson] = useState<LessonPlan | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const response = await fetch('/api/generate-lesson', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headline, locale, gradeLevel, subject }),
      });

      if (!response.ok) {
        const data = (await response.json()) as { error?: string };
        throw new Error(data.error ?? 'Lesson generation failed.');
      }

      const data = (await response.json()) as { lesson: LessonPlan };
      setLesson(data.lesson);
    } catch (submitError) {
      setError(submitError instanceof Error ? submitError.message : 'Something went wrong.');
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="generator-section" id="demo">
      <div className="section-intro">
        <p className="eyebrow">Prototype demo</p>
        <h2>Generate a lesson from a current event in seconds.</h2>
        <p className="section-copy">
          This is the first working slice of RealSTEM: a teacher enters a headline, chooses a grade band,
          and gets a draft lesson back from the app.
        </p>
      </div>

      <div className="generator-grid">
        <form className="generator-form" onSubmit={handleSubmit}>
          <label>
            News headline
            <input
              type="text"
              value={headline}
              onChange={(event) => setHeadline(event.target.value)}
              placeholder="Paste a current news story"
            />
          </label>

          <div className="field-row">
            <label>
              Locale
              <select value={locale} onChange={(event) => setLocale(event.target.value as LessonInput['locale'])}>
                <option value="India">India</option>
                <option value="US">US</option>
                <option value="Global">Global</option>
              </select>
            </label>

            <label>
              Grade band
              <select
                value={gradeLevel}
                onChange={(event) => setGradeLevel(event.target.value as LessonInput['gradeLevel'])}
              >
                <option value="Middle School">Middle School</option>
                <option value="High School">High School</option>
              </select>
            </label>
          </div>

          <label>
            Subject
            <select value={subject} onChange={(event) => setSubject(event.target.value as LessonInput['subject'])}>
              <option value="Physics">Physics</option>
              <option value="Chemistry">Chemistry</option>
              <option value="Biology">Biology</option>
              <option value="Mathematics">Mathematics</option>
              <option value="Computer Science">Computer Science</option>
              <option value="Earth Science">Earth Science</option>
            </select>
          </label>

          <div className="example-row">
            {exampleHeadlines.map((example) => (
              <button key={example} type="button" className="example-chip" onClick={() => setHeadline(example)}>
                {example}
              </button>
            ))}
          </div>

          <button className="primary-action generator-submit" type="submit" disabled={isLoading}>
            {isLoading ? 'Generating lesson...' : 'Generate lesson'}
          </button>
          {error ? <p className="form-message error">{error}</p> : null}
        </form>

        <aside className="generator-output">
          {lesson ? (
            <>
              <div className="panel-header">
                <span>{lesson.gradeLevel}</span>
                <span className="status-pill">Draft ready</span>
              </div>
              <h3>{lesson.topic}</h3>
              <p>{lesson.relevanceSummary}</p>
              <div className="output-block">
                <h4>Standards</h4>
                <ul>
                  {lesson.standards.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
              <div className="output-block">
                <h4>Lesson flow</h4>
                <ol>
                  {lesson.lessonFlow.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ol>
              </div>
              <div className="output-block">
                <h4>Student task</h4>
                <p>{lesson.studentTask}</p>
              </div>
              <div className="output-block">
                <h4>Teacher notes</h4>
                <ul>
                  {lesson.teacherNotes.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p className="eyebrow">Teacher review</p>
              <h3>Your lesson draft will appear here.</h3>
              <p>
                The generator returns the lesson structure, standards, activities, and teacher notes so the draft
                can be reviewed before students see it.
              </p>
            </div>
          )}
        </aside>
      </div>
    </section>
  );
}