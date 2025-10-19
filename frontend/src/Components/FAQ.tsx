import React, { useState } from 'react';

interface FAQProps {
  question: string;
  answer: string;
}

export default function FAQ({ question, answer }: FAQProps) {
  const [isOpen, setIsOpen] = useState(false);

  const toggleFAQ = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="faq-item">
      <h3 
        className="faq-question" 
        onClick={toggleFAQ}
        style={{ cursor: 'pointer' }}
      >
        {question}
      </h3>
      {isOpen && (
        <p className="faq-answer">{answer}</p>
      )}
    </div>
  );
}