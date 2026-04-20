import React, { useEffect, useState } from 'react';

interface Career {
  id: string;
  title: string;
  description: string;
  salary: string;
  skills: string[];
}

const CareerExplorer: React.FC = () => {
  const [careers, setCareers] = useState<Career[]>([]);
  const [selectedCareer, setSelectedCareer] = useState<Career | null>(null);

  useEffect(() => {
    // Fetch careers
  }, []);

  return (
    <div className="career-explorer">
      <h1>Career Explorer</h1>
      <div className="career-container">
        <div className="career-list">
          {careers.map((career) => (
            <div
              key={career.id}
              className="career-item"
              onClick={() => setSelectedCareer(career)}
            >
              <h3>{career.title}</h3>
            </div>
          ))}
        </div>
        {selectedCareer && (
          <div className="career-detail">
            <h2>{selectedCareer.title}</h2>
            <p>{selectedCareer.description}</p>
            <p>Salary: {selectedCareer.salary}</p>
            <h4>Required Skills:</h4>
            <ul>
              {selectedCareer.skills.map((skill, idx) => (
                <li key={idx}>{skill}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};

export default CareerExplorer;
