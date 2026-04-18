import { NextResponse } from 'next/server';
import { generateLessonPlan, type LessonInput } from '@/lib/lesson-generator';

const allowedLocales: LessonInput['locale'][] = ['India', 'US', 'Global'];
const allowedGrades: LessonInput['gradeLevel'][] = ['Middle School', 'High School'];
const allowedSubjects: LessonInput['subject'][] = [
  'Physics',
  'Chemistry',
  'Biology',
  'Mathematics',
  'Computer Science',
  'Earth Science',
];

function isString(value: unknown): value is string {
  return typeof value === 'string' && value.trim().length > 0;
}

export async function POST(request: Request) {
  const body: Partial<LessonInput> = await request.json();

  if (
    !isString(body.headline) ||
    !body.locale ||
    !body.gradeLevel ||
    !body.subject ||
    !allowedLocales.includes(body.locale) ||
    !allowedGrades.includes(body.gradeLevel) ||
    !allowedSubjects.includes(body.subject)
  ) {
    return NextResponse.json(
      {
        error: 'Provide headline, locale, gradeLevel, and subject using one of the supported values.',
      },
      { status: 400 },
    );
  }

  const lesson = generateLessonPlan({
    headline: body.headline.trim(),
    locale: body.locale,
    gradeLevel: body.gradeLevel,
    subject: body.subject,
  });

  return NextResponse.json({ lesson });
}