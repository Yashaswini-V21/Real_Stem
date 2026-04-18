export type LessonInput = {
  headline: string;
  locale: 'India' | 'US' | 'Global';
  gradeLevel: 'Middle School' | 'High School';
  subject: 'Physics' | 'Chemistry' | 'Biology' | 'Mathematics' | 'Computer Science' | 'Earth Science';
};

export type LessonPlan = {
  topic: string;
  headline: string;
  locale: LessonInput['locale'];
  gradeLevel: LessonInput['gradeLevel'];
  subject: LessonInput['subject'];
  relevanceSummary: string;
  standards: string[];
  lessonFlow: string[];
  studentTask: string;
  teacherNotes: string[];
};

const subjectAngles: Record<
  LessonInput['subject'],
  { topic: string; standards: string[]; flow: string[]; task: string; notes: string[] }
> = {
  Physics: {
    topic: 'Forces, motion, and real-world systems',
    standards: ["Newton's laws", 'Energy transfer', 'Modeling motion'],
    flow: [
      'Identify the forces and constraints in the news event.',
      'Map the event to motion, energy, or safety tradeoffs.',
      'Run a quick calculation with a real number from the story.',
      'Discuss whether the system is good enough for public use.',
    ],
    task: 'Students calculate the relevant forces or energy changes and propose a safer design test.',
    notes: ['Use units explicitly.', 'Ask students to justify assumptions.', 'Connect results to everyday decisions.'],
  },
  Chemistry: {
    topic: 'Materials, reactions, and environmental change',
    standards: ['Reaction rates', 'Matter and properties', 'Environmental systems'],
    flow: [
      'Identify the substances, materials, or pollutants in the story.',
      'Explain the chemistry behind the observed change.',
      'Estimate how scale changes affect outcomes.',
      'Evaluate the environmental or health impact.',
    ],
    task: 'Students model the reaction, mixture, or contamination issue using a simple data table.',
    notes: ['Tie to labs when possible.', 'Highlight safety and measurement.', 'Use local examples if available.'],
  },
  Biology: {
    topic: 'Living systems, health, and adaptation',
    standards: ['Ecosystems', 'Genetics and heredity', 'Human body systems'],
    flow: [
      'Identify the living system or health issue in the headline.',
      'Trace how the biological process works.',
      'Compare short-term and long-term impacts.',
      'Discuss prevention, intervention, or resilience.',
    ],
    task: 'Students build a cause-and-effect chain and recommend one intervention.',
    notes: ['Avoid sensationalism.', 'Check for culturally sensitive framing.', 'Encourage evidence-based reasoning.'],
  },
  Mathematics: {
    topic: 'Statistics, scale, and quantitative reasoning',
    standards: ['Ratios and proportions', 'Statistics', 'Functions and modeling'],
    flow: [
      'Extract the numbers from the article.',
      'Choose the right representation: percent, ratio, graph, or probability.',
      'Estimate the scale of the impact.',
      'Interpret what the result means in context.',
    ],
    task: 'Students build a quick model or graph and explain whether the trend is meaningful.',
    notes: ['Use clean numbers from the story.', 'Show one calculation by hand.', 'Ask for interpretation, not just answers.'],
  },
  'Computer Science': {
    topic: 'Algorithms, automation, and AI reliability',
    standards: ['Algorithms', 'Data representation', 'Ethics in computing'],
    flow: [
      'Identify the automated system or software in the story.',
      'Explain the inputs, outputs, and failure modes.',
      'Connect accuracy, bias, and edge cases.',
      'Design a test plan for safer deployment.',
    ],
    task: 'Students sketch a simple decision rule or test cases for a small ML system.',
    notes: [
      'Use concrete examples of false positives and false negatives.',
      'Discuss fairness and reliability.',
      'Keep coding optional but hands-on.',
    ],
  },
  'Earth Science': {
    topic: 'Weather, climate, and planetary systems',
    standards: ['Weather systems', 'Climate patterns', 'Earth resources'],
    flow: [
      'Locate the environmental or planetary signal in the headline.',
      'Describe the system at local and global scales.',
      'Compare short-term weather effects with long-term climate patterns.',
      'Discuss adaptation, preparedness, or monitoring.',
    ],
    task: 'Students analyze a map, chart, or trend and recommend one preparedness action.',
    notes: ['Link to local geography.', 'Use graphs whenever possible.', 'Connect science to community resilience.'],
  },
};

function inferTopic(headline: string): string {
  const lowerHeadline = headline.toLowerCase();

  if (lowerHeadline.includes('moon') || lowerHeadline.includes('rocket') || lowerHeadline.includes('orbit')) {
    return 'Orbital mechanics and space exploration';
  }

  if (lowerHeadline.includes('recall') || lowerHeadline.includes('autopilot') || lowerHeadline.includes('crash')) {
    return 'Machine learning safety and system reliability';
  }

  if (lowerHeadline.includes('pollution') || lowerHeadline.includes('emissions') || lowerHeadline.includes('climate')) {
    return 'Environmental science and systems change';
  }

  if (lowerHeadline.includes('outbreak') || lowerHeadline.includes('virus') || lowerHeadline.includes('health')) {
    return 'Health systems and biological spread';
  }

  return 'A real-world STEM system hiding inside the news';
}

export function generateLessonPlan(input: LessonInput): LessonPlan {
  const subjectContent = subjectAngles[input.subject];
  const topic = inferTopic(input.headline);
  const relevanceSummary = `This ${input.locale} story gives ${input.gradeLevel.toLowerCase()} students a concrete example of ${subjectContent.topic.toLowerCase()} using the headline: ${input.headline}.`;

  return {
    topic,
    headline: input.headline,
    locale: input.locale,
    gradeLevel: input.gradeLevel,
    subject: input.subject,
    relevanceSummary,
    standards: subjectContent.standards,
    lessonFlow: subjectContent.flow,
    studentTask: subjectContent.task,
    teacherNotes: subjectContent.notes,
  };
}