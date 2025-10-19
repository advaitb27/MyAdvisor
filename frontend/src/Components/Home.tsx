import React from 'react';
import ChatBar from './ChatBar';
import FAQ from './FAQ';
import ShinyText from './ShinyText';

const FAQs = [
  {
    question: "Who can use myAdvisor?",
    answer: "Any UW student can use this tool to plan their academic journey. It's a great resource for students who are unsure about their major or want to explore different options."
  },
  {
    question: "Does MyAdvisor cost money or need a subscription?",
    answer: "Yes! This tool is free to use and will always be free. You can use it as many times as you want."
  },
  {
    question: "How does myAdvisor help UW students?",
    answer: "This tool uses AI to help you plan your academic journey. You can ask it questions about your interests, skills, and career goals, and it will help you find the best major for you."
  },
  {
    question: "Are the recommendations accurate?",
    answer: "Yes! This tool is accurate and up-to-date. It's a great resource for students who are unsure about their major or want to explore different options."
  }
]

const Home = () => {
  const scrollToAbout = () => {
    const aboutSection = document.getElementById('about-section');
    if (aboutSection) {
      aboutSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  const scrollToFAQs = () => {
    const faqsSection = document.getElementById('faqs-section');
    if (faqsSection) {
      faqsSection.scrollIntoView({ behavior: 'smooth' });
    }
  };

  return (
    <div>
      <div className='Navigation Bar'>
        <button onClick={scrollToAbout}>About</button>
        <button onClick={scrollToFAQs}>FAQs</button>
      </div>
      
      <div className='hero-section'>
        <h1>MyAdvisor</h1>
        24/7 AI powered academic and course planning support for UW students
        <div>
          <ChatBar />
        </div>
      </div>
      <h2 id="about-section">854 Degrees. 180 Majors. 50,000 Students. <ShinyText text="One Tool." speed={2} />
      </h2>
      
      <p>MyPlan AI Advisor is your 24/7 academic planning companion. Our AI-powered platform helps 
        UW students navigate over 854 degree programs and 180 majors to plan and prepare for their 
        educational journey.
        <br></br>
        <br></br>
        Get personalized course recommendations, explore majors that match your interests, and 
        create a clear path to graduation. Whether you're choosing a major or planning next 
        semester's schedule, MyPlan AI Advisor provides instant, intelligent guidance whenever you need it.</p>
      
      <h2 id="faqs-section">FAQs</h2>
      <div className="faqs-container">
        {FAQs.map((faq, index) => (
          <FAQ key={index} question={faq.question} answer={faq.answer} />
        ))}
      </div>
    </div>
  );
};

export default Home;
