import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const CATEGORIES = ['Todos', 'Tecnologia', 'Negócios', 'Design', 'Marketing'];

const Courses = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [courses, setCourses] = useState([]);
  const [filteredCourses, setFilteredCourses] = useState([]);
  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [activeCategory, setActiveCategory] = useState('Todos');
  const navigate = useNavigate();

  useEffect(() => {
    fetch('http://localhost:5000/get-courses')
      .then((res) => res.json())
      .then((data) => {
        setCourses(data);
        setFilteredCourses(data);
      })
      .catch((err) => console.error('Error fetching courses:', err));
  }, []);

  useEffect(() => {
    const filtered = courses.filter((course) =>
      course.name.toLowerCase().includes(searchTerm.toLowerCase())
    );
    setFilteredCourses(filtered);
  }, [searchTerm, courses]);

  const nextImage = () =>
    setCurrentImageIndex((i) => (i + 1) % Math.max(courses.length, 1));
  const prevImage = () =>
    setCurrentImageIndex((i) => (i === 0 ? courses.length - 1 : i - 1));

  const heroItem = courses[currentImageIndex];

  return (
    <div className="bg-surface text-on-surface min-h-screen selection:bg-secondary-fixed selection:text-on-secondary-fixed">
      {/* TopNavBar */}
      <nav className="fixed top-0 w-full z-50 bg-slate-50/80 backdrop-blur-xl shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
        <div className="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto">
          <div className="text-2xl font-bold text-blue-900 font-headline">EducaMundo</div>
          <div className="hidden md:flex items-center gap-8">
            <a className="text-slate-500 font-medium hover:text-blue-700 transition-colors cursor-pointer" href="#">
              Meus Cursos
            </a>
            <a className="text-blue-900 font-bold transition-colors cursor-pointer" href="#">
              Explorar
            </a>
            <a className="text-slate-500 font-medium hover:text-blue-700 transition-colors cursor-pointer" href="#">
              Certificados
            </a>
          </div>
          <div className="flex items-center gap-4">
            <button className="p-2 text-blue-900 hover:bg-surface-container rounded-full transition-colors">
              <span className="material-symbols-outlined">notifications</span>
            </button>
            <button className="p-2 text-blue-900 hover:bg-surface-container rounded-full transition-colors">
              <span className="material-symbols-outlined">account_circle</span>
            </button>
          </div>
        </div>
        <div className="bg-slate-200/50 h-px w-full" />
      </nav>

      <main className="pt-20">
        {/* Hero Carousel */}
        {heroItem ? (
          <section className="px-8 mt-6">
            <div className="max-w-screen-2xl mx-auto relative rounded-xl overflow-hidden aspect-[21/9] md:aspect-[3/1]">
              <img
                src={heroItem.img}
                alt={heroItem.name}
                className="absolute inset-0 w-full h-full object-cover opacity-40"
              />
              <div className="absolute inset-0 bg-gradient-to-r from-primary via-primary/60 to-transparent" />
              <div className="absolute inset-0 flex items-center px-12 md:px-20">
                <div className="max-w-3xl">
                  <span className="inline-block px-3 py-1 bg-tertiary-fixed-dim text-on-tertiary-fixed text-xs font-bold rounded-full mb-4 tracking-widest uppercase">
                    Destaque
                  </span>
                  <h1 className="text-4xl md:text-6xl font-extrabold text-white leading-tight mb-6 tracking-tighter font-headline">
                    {heroItem.name}
                  </h1>
                  <div className="flex gap-4">
                    <button
                      onClick={() => navigate(`/course/${heroItem.id}`)}
                      className="px-8 py-3 bg-white text-primary font-bold rounded-md hover:-translate-y-0.5 transition-transform duration-200 active:scale-95"
                    >
                      Acessar Curso
                    </button>
                    <button className="px-8 py-3 border border-white/20 text-white font-bold rounded-md backdrop-blur-sm hover:bg-white/10 transition-colors">
                      Ver Detalhes
                    </button>
                  </div>
                </div>
              </div>
              {/* Prev/Next arrows */}
              <button
                onClick={prevImage}
                className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 backdrop-blur rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors z-20"
              >
                <span className="material-symbols-outlined">chevron_left</span>
              </button>
              <button
                onClick={nextImage}
                className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-white/20 backdrop-blur rounded-full flex items-center justify-center text-white hover:bg-white/30 transition-colors z-20"
              >
                <span className="material-symbols-outlined">chevron_right</span>
              </button>
              {/* Dots */}
              <div className="absolute bottom-8 right-12 flex gap-3 z-20">
                {courses.slice(0, 5).map((_, i) => (
                  <button
                    key={i}
                    onClick={() => setCurrentImageIndex(i)}
                    className={`h-1 rounded-full transition-all ${
                      i === currentImageIndex ? 'w-12 bg-white' : 'w-12 bg-white/30'
                    }`}
                  />
                ))}
              </div>
            </div>
          </section>
        ) : null}

        {/* Search & Filter Bar */}
        <section className="px-8 mt-12 mb-16">
          <div className="max-w-screen-2xl mx-auto">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-8">
              <div className="max-w-xl flex-1">
                <label className="block text-sm font-bold text-primary mb-3 uppercase tracking-wider">
                  O que você quer aprender hoje?
                </label>
                <div className="relative">
                  <span className="material-symbols-outlined absolute left-4 top-1/2 -translate-y-1/2 text-outline">
                    search
                  </span>
                  <input
                    type="text"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-12 pr-4 py-4 bg-surface-container-highest border-none rounded-xl focus:outline-none focus:ring-2 focus:ring-secondary/20 transition-all font-body"
                    placeholder="Busque por cursos, autores ou temas..."
                  />
                </div>
              </div>
              <div className="flex gap-2 overflow-x-auto hide-scrollbar pb-2">
                {CATEGORIES.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => setActiveCategory(cat)}
                    className={`whitespace-nowrap px-6 py-3 rounded-full font-semibold text-sm transition-colors ${
                      activeCategory === cat
                        ? 'bg-secondary text-white font-bold shadow-sm'
                        : 'bg-surface-container-low text-on-surface-variant hover:bg-surface-container-high'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* Courses Grid */}
        <section className="px-8 mb-24">
          <div className="max-w-screen-2xl mx-auto">
            <div className="flex items-center justify-between mb-10">
              <h2 className="text-3xl font-extrabold text-primary tracking-tight font-headline">
                Todos os Cursos
              </h2>
              <button className="text-secondary font-bold flex items-center gap-2 hover:gap-3 transition-all">
                Ver mais categorias{' '}
                <span className="material-symbols-outlined">arrow_forward</span>
              </button>
            </div>

            {filteredCourses.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
                {filteredCourses.map((course) => (
                  <div
                    key={course.id}
                    onClick={() => navigate(`/course/${course.id}`)}
                    className="group bg-surface-container-lowest rounded-xl overflow-hidden transition-all duration-300 hover:-translate-y-2 cursor-pointer shadow-sm hover:shadow-md"
                  >
                    <div className="aspect-video relative overflow-hidden">
                      <img
                        src={course.img}
                        alt={course.name}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                      />
                      <div className="absolute top-4 left-4 bg-white/90 backdrop-blur px-3 py-1 rounded-full shadow-sm">
                        <span className="text-[10px] font-bold text-primary uppercase">Curso</span>
                      </div>
                    </div>
                    <div className="p-6">
                      <h3 className="font-bold text-lg text-primary mb-2 line-clamp-2 font-headline">
                        {course.name}
                      </h3>
                      <div className="flex items-center gap-2 mb-4">
                        <span
                          className="material-symbols-outlined text-tertiary-fixed-dim text-lg"
                          style={{ fontVariationSettings: "'FILL' 1" }}
                        >
                          star
                        </span>
                        <span className="text-sm font-bold text-primary">4.8</span>
                        <span className="text-xs text-outline">(alunos)</span>
                      </div>
                      <div className="flex items-center justify-between pt-4 border-t border-outline-variant/10">
                        <span className="text-xl font-extrabold text-primary">Gratuito</span>
                        <button className="p-2 bg-secondary/10 text-secondary rounded-lg hover:bg-secondary hover:text-white transition-colors">
                          <span className="material-symbols-outlined">play_arrow</span>
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <p className="col-span-full text-center text-on-surface-variant py-16">
                Nenhum curso encontrado.
              </p>
            )}
          </div>
        </section>

        {/* CTA Block */}
        <section className="px-8 mb-24">
          <div className="max-w-screen-2xl mx-auto bg-surface-container-low rounded-3xl p-12 md:p-20 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-1/3 h-full bg-secondary-container/5 -skew-x-12 translate-x-20" />
            <div className="relative z-10 max-w-2xl">
              <h2 className="text-4xl font-extrabold text-primary mb-6 leading-tight font-headline">
                Pronto para dar o próximo passo na sua carreira?
              </h2>
              <p className="text-on-surface-variant text-lg mb-8 leading-relaxed">
                Acesso vitalício e conteúdo de qualidade em todos os cursos da plataforma.
              </p>
              <button className="px-10 py-4 bg-primary text-white font-bold rounded-md shadow-lg shadow-primary/20 hover:-translate-y-0.5 transition-transform">
                Começar Agora
              </button>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-slate-100 w-full py-12">
        <div className="flex flex-col items-center gap-6 px-4 max-w-screen-2xl mx-auto">
          <div className="flex gap-8 flex-wrap justify-center text-xs tracking-wide">
            <a className="text-slate-500 hover:text-blue-700 transition-all duration-300" href="#">
              Termos de Uso
            </a>
            <a className="text-slate-500 hover:text-blue-700 transition-all duration-300" href="#">
              Privacidade
            </a>
            <a className="text-slate-500 hover:text-blue-700 transition-all duration-300" href="#">
              Suporte
            </a>
            <a className="text-slate-500 hover:text-blue-700 transition-all duration-300" href="#">
              Trabalhe Conosco
            </a>
          </div>
          <div className="w-full max-w-md h-px bg-slate-200" />
          <p className="text-slate-500 text-xs tracking-wide text-center">
            © 2024 EducaMundo - Transformando o Futuro através da Educação. Todos os direitos
            reservados.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Courses;
