import React, { useEffect, useState } from 'react';
import { useNavigate, useParams, Link } from 'react-router-dom';
import { FaRegUserCircle } from 'react-icons/fa';
import { IoIosHome, IoMdMenu } from 'react-icons/io';

const Content = () => {
  const { id } = useParams();
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(true);
  const [contentData, setContentData] = useState([]);
  const [isExpanded, setIsExpanded] = useState(false);
  const navigate = useNavigate();

  const handleExpandClick = () => {
    setIsExpanded((prev) => !prev);
  };

  const createHtmlElement = (item) => {
  const { type_content, content } = item;

  switch (type_content) {
    case 'video':
      return (
        <div className="flex items-center justify-center iframe-container w-full h-full">
          <iframe
            className="w-6/12 min-h-full"
            src={`https://www.youtube.com/embed/${content}`}
            title="YouTube Video"
            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
            allowFullScreen
          ></iframe>
        </div>
      );
    case 'transcription':
      return (
        <div className="flex flex-col items-center justify-start w-full">
          <p className={`text-xl`}>{content}<br /><br /></p>
        </div>
      );
    case 'paragraph':
      return <p className="paragraph">{content}</p>;
    default:
      return <span className="default">{content}</span>;
  }
};

const renderElements = (items) => {
  const groupedElements = {
    preVideos: [],
    videos: [],
    postVideos: [],
  };

  // Group elements into preVideos, videos, and postVideos
  let foundVideo = false;
  items.forEach(item => {
    if (item.type_content === 'video') {
      foundVideo = true;
      groupedElements.videos.push(item);
    } else if (!foundVideo) {
      groupedElements.preVideos.push(item);
    } else {
      groupedElements.postVideos.push(item);
    }
  });

  // Render elements in the desired order
  return (
    <>
      {groupedElements.preVideos.map((item, index) => (
        <div key={`pre-${index}`}>{createHtmlElement(item)}</div>
      ))}
      {groupedElements.videos.map((item, index) => (
        <div key={`video-${index}`}>{createHtmlElement(item)}</div>
      ))}
      {groupedElements.postVideos.map((item, index) => (
        <div key={`post-${index}`}>{createHtmlElement(item)}</div>
      ))}
    </>
  );
};


  const handleMenuClick = (topicId) => {
    setLoading(true);
    fetch(`http://localhost:5000/get-content/${topicId}`)
      .then((response) => response.json())
      .then((data) => {
        setContentData(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error('Erro ao buscar conteúdo:', error);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetch(`http://localhost:5000/get-topics/${id}`)
      .then((response) => response.json())
      .then((data) => {
        setCourses(data);
        setLoading(false);

        // Solicitar o conteúdo do primeiro tópico por padrão
        if (data.length > 0) {
          handleMenuClick(data[0].id); // Chamar o handleMenuClick com o id do primeiro tópico
        }
      })
      .catch((error) => {
        console.error('Erro ao buscar curso:', error);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return <p>Carregando...</p>;
  }

  if (!courses || courses.length === 0) {
    return <p>Curso não encontrado.</p>;
  }

  return (
    <div className="bg-gray-400 w-screen h-screen flex flex-col max-h-screen overflow-hidden">
      {/* Navbar */}
      <nav className="flex items-center justify-between gap-4 p-4 w-full px-6 bg-gray-800 text-gray-300">
        <p
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          className="text-4xl hover:text-white hover:cursor-pointer"
        >
          <IoMdMenu />
        </p>
        <Link to="/" className="text-4xl hover:text-white hover:cursor-pointer">
          <IoIosHome />
        </Link>
        <Link to="/profile" className="text-4xl hover:text-white">
          <FaRegUserCircle />
        </Link>
      </nav>

      {/* Layout */}
      <div className="flex flex-grow max-h-full overflow-hidden">
        {/* Sidebar */}
        <div
          className={`transition-all duration-300 ease-in-out ${
            isMenuOpen ? 'min-w-[20vw] px-4 py-4' : 'w-0 overflow-hidden'
          } bg-slate-700 text-white h-full flex flex-col justify-start overflow-y-auto`}
        >
          {courses.map((course) => (
            <div
              key={course.id}
              className="bg-slate-900 w-full p-4 my-2 rounded-md hover:bg-slate-500 hover:cursor-pointer"
              onClick={() => handleMenuClick(course.id)}
            >
              <p className="text-lg font-semibold line-clamp-2 overflow-hidden text-ellipsis whitespace-nowrap">{course.name}</p>
            </div>
          ))}
        </div>

        {/* Content */}
        <div className="flex flex-grow pt-4 pb-4 px-4 bg-slate-400">
          <div className="flex flex-col items-center">
            {/* Div para o vídeo */}
            <div className="flex items-center justify-center w-full min-h-80 ">
              {contentData
                .filter((item) => item.type_content === 'video')
                .map((item, index) => (
                  <React.Fragment key={index}>{createHtmlElement(item)}</React.Fragment>
                ))}
            </div>
            <h2 className='text-3xl py-4 underline'>Transcrição</h2>
            {/* Div para transcrições */}
            <div
              className={`flex flex-col items-center justify-start w-full px-8 transition-all duration-300 ease-in-out ${
                isExpanded ? 'max-h-full overflow-y-auto' : 'max-h-20 overflow-hidden'
              }`}
            >
              {contentData
                .filter((item) => item.type_content !== 'video')
                .map((item, index) => (
                  <React.Fragment key={index}>{createHtmlElement(item)}</React.Fragment>
                ))}
            </div>

            {/* Botão para expandir */}
            <button
              onClick={handleExpandClick}
              className="mt-4 text-blue-800 hover:underline"
            >
              {isExpanded ? 'Mostrar menos' : 'Mostrar mais'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Content;
