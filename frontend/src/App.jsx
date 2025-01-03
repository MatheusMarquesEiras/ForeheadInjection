import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Courses from './pages/Courses';
import Content from './pages/Content';

const App = () => {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Courses />} />
        <Route path="/course/:id" element={<Content />} /> {/* Dynamic route */}
      </Routes>
    </Router>
  );
};

export default App;
