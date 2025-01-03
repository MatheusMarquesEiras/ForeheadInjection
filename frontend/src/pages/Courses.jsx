import React, { useState, useEffect } from 'react';
import { FaRegUserCircle, FaInstagram, FaLinkedin, FaGithub } from 'react-icons/fa';
import { IoIosHome } from 'react-icons/io';
import { useNavigate, Link } from 'react-router-dom';

const Courses = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [images, setImages] = useState([]);
  const navigate = useNavigate(); // Hook for navigation

  useEffect(() => {
    // Fetch courses from API
    fetch('http://localhost:5000/get-courses')
      .then((response) => response.json())
      .then((data) => {
        setCourses(data); // Save all courses
        setFilteredCourses(data); // Initially, show all courses
        setImages(data); // Use the same data for the carousel
      })
      .catch((error) => console.error('Error fetching courses:', error));
  }, []);

  useEffect(() => {
    // Filter courses dynamically based on search term
    const filtered = courses.filter((course) =>
      course.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCourses(filtered);
  }, [searchTerm, courses]);

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const nextImage = () => {
    setCurrentImageIndex((prevIndex) => (prevIndex + 1) % images.length);
  };

  const prevImage = () => {
    setCurrentImageIndex((prevIndex) =>
      prevIndex === 0 ? images.length - 1 : prevIndex - 1
    );
  };

  const handleCourseClick = (id) => {
    navigate(`/course/${id}`); // Navigate to the route with the course ID
  };

  return (
    <div className="w-full min-h-screen bg-gray-400">
      <nav className="flex items-center justify-between gap-4 p-4 w-full px-6 bg-gray-800 text-gray-300">
        <Link
          to="/"
          className="text-4xl hover:text-white hover:cursor-pointer"
        >
          <IoIosHome />
        </Link>
        <Link to="/profile" className="text-4xl hover:text-white">
          <FaRegUserCircle />
        </Link>
      </nav>
      <div className="relative w-full min-h-[50vh]">
        {images.length > 0 ? (
          <img
            src={images[currentImageIndex].img}
            alt={images[currentImageIndex].name}
            className="absolute top-0 left-0 w-full h-full object-fill"
          />
        ) : (
          <p>Carregando imagens...</p>
        )}
        <button
          onClick={prevImage}
          className="absolute left-0 top-0 h-full w-16 flex items-center justify-center bg-white bg-opacity-80 text-6xl"
        >
          &#8249;
        </button>
        <button
          onClick={nextImage}
          className="absolute right-0 top-0 h-full w-16 flex items-center justify-center bg-white bg-opacity-80 text-6xl"
        >
          &#8250;
        </button>
      </div>

      {/* Search Bar */}
      <div className="flex items-center justify-center w-full">
        <h1 className="text-6xl pt-6 font-mono text-wrap text-center">Nossos Cursos</h1>
      </div>
      <form className="flex items-center justify-center ml-auto w-full pt-8 pb-14">
        <input
          type="text"
          value={searchTerm}
          onChange={handleSearchChange}
          className="py-2 px-4 border rounded-full w-8/12 sm:w-6/12 lg:h-5/6"
          placeholder="O que vamos aprender hoje?"
        />
      </form>

      {/* Filtered Courses Grid */}
      <div className="flex items-start justify-center w-full min-h-[70vh] pt-7">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 w-5/6 overflow-x-hidden max-h-[70vh]">
          {filteredCourses.length > 0 ? (
            filteredCourses.map((course) => (
              <div key={course.id} className="w-full h-48 bg-gray-200">
                <img
                  src={course.img}
                  alt={course.name}
                  className="w-full h-full object-cover cursor-pointer"
                  onClick={() => handleCourseClick(course.id)} // Navigate on click
                />
              </div>
            ))
          ) : (
            <p className="col-span-full text-center">Nenhum curso encontrado.</p>
          )}
        </div>
      </div>
      <div className="flex items-center justify-center my-4 w-full h-12 mt-24">
        <div className="flex items-center justify-center w-1/12 text-4xl ">
          <a href="#" className="text-black hover:text-white cursor-pointer">
            <FaGithub />
          </a>
          <a href="#" className="text-black hover:text-white cursor-pointer mx-8">
            <FaInstagram />
          </a>
          <a href="#" className="text-black hover:text-white cursor-pointer">
            <FaLinkedin />
          </a>
        </div>
      </div>
      <footer className="w-full flex items-center justify-center py-4 bg-gray-600">
        Copyright © 2024 EducaMundo
      </footer>
    </div>
  );
};

export default Courses;
