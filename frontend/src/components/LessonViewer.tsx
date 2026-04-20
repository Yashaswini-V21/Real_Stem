import React, { useEffect, useState } from 'react';
import { Lesson } from '../types/lesson';

interface LessonViewerProps {
  lessonId?: string;
}

const LessonViewer: React.FC<LessonViewerProps> = ({ lessonId }) => {
  const [lesson, setLesson] = useState<Lesson | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch lesson
    setLoading(false);
  }, [lessonId]);

  return (
    <div className="lesson-viewer">
      <h1>Lesson Viewer</h1>
      {loading ? (
        <div>Loading...</div>
      ) : lesson ? (
        <div className="lesson-content">
          <h2>{lesson.title}</h2>
          <p>{lesson.description}</p>
          <div className="content">{lesson.content}</div>
        </div>
      ) : (
        <div>No lesson selected</div>
      )}
    </div>
  );
};

export default LessonViewer;
