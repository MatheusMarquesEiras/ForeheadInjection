import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';

const Content = () => {
  const { id } = useParams();
  const [topics, setTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [contentData, setContentData] = useState([]);
  const [selectedTopicId, setSelectedTopicId] = useState(null);
  const [selectedTopicName, setSelectedTopicName] = useState('');
  const [activityData, setActivityData] = useState(null);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [answerSubmitted, setAnswerSubmitted] = useState(false);

  const handleTopicClick = (topic) => {
    setLoading(true);
    setSelectedTopicId(topic.id);
    setSelectedTopicName(topic.name);
    setSelectedAnswer(null);
    setAnswerSubmitted(false);
    setActivityData(null);

    fetch(`http://localhost:5000/get-content/${topic.id}`)
      .then((res) => res.json())
      .then((data) => {
        setContentData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Erro ao buscar conteúdo:', err);
        setLoading(false);
      });

    fetch(`http://localhost:5000/get-activity/${topic.id}`)
      .then((res) => res.json())
      .then((data) => setActivityData(data && data.question ? data : null))
      .catch(() => setActivityData(null));
  };

  useEffect(() => {
    fetch(`http://localhost:5000/get-topics/${id}`)
      .then((res) => res.json())
      .then((data) => {
        setTopics(data);
        setLoading(false);
        if (data.length > 0) {
          handleTopicClick(data[0]);
        }
      })
      .catch((err) => {
        console.error('Erro ao buscar tópicos:', err);
        setLoading(false);
      });
  }, [id]);

  const videoItem = contentData.find((item) => item.type_content === 'video');
  const transcriptionItems = contentData.filter(
    (item) => item.type_content === 'transcription' || item.type_content === 'paragraph'
  );

  if (!loading && topics.length === 0) {
    return (
      <div className="min-h-screen bg-surface flex items-center justify-center">
        <p className="text-on-surface-variant">Curso não encontrado.</p>
      </div>
    );
  }

  return (
    <div className="bg-surface text-on-surface overflow-x-hidden">
      {/* Sidebar */}
      <aside
        className={`h-screen w-72 fixed left-0 top-0 bg-slate-50 flex flex-col p-6 gap-2 z-40 transition-transform duration-300 ${
          isMenuOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
        }`}
      >
        <div className="mb-8">
          <div className="text-xl font-bold text-blue-900 font-headline mb-4">EducaMundo</div>
          <div className="overflow-hidden">
            <h3 className="text-slate-700 font-semibold font-headline text-sm leading-tight line-clamp-2">
              {topics[0]?.course_name || 'Meus Cursos'}
            </h3>
            <p className="text-slate-500 text-xs font-medium mt-0.5">
              {topics.length} tópico{topics.length !== 1 ? 's' : ''}
            </p>
          </div>
        </div>

        <nav className="flex-1 flex flex-col gap-1 overflow-y-auto hide-scrollbar">
          {topics.map((topic) => (
            <div
              key={topic.id}
              onClick={() => {
                handleTopicClick(topic);
                setIsMenuOpen(false);
              }}
              className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-all font-headline text-sm ${
                selectedTopicId === topic.id
                  ? 'bg-white text-blue-900 font-bold shadow-sm'
                  : 'text-slate-500 hover:bg-slate-200/50 hover:translate-x-1'
              }`}
            >
              <span className="material-symbols-outlined shrink-0 text-[20px]">
                {selectedTopicId === topic.id ? 'menu_book' : 'play_circle'}
              </span>
              <span className="line-clamp-2 leading-snug">{topic.name}</span>
            </div>
          ))}
        </nav>

        <Link
          to="/"
          className="mt-auto flex items-center justify-center gap-2 py-3 px-4 bg-surface-container-highest text-primary font-bold rounded-md hover:bg-surface-container-high transition-colors text-sm"
        >
          <span className="material-symbols-outlined text-[18px]">arrow_back</span>
          Voltar ao Painel
        </Link>
      </aside>

      {/* Mobile overlay */}
      {isMenuOpen && (
        <div
          className="fixed inset-0 bg-black/40 z-30 md:hidden"
          onClick={() => setIsMenuOpen(false)}
        />
      )}

      {/* TopNavBar */}
      <header className="fixed top-0 w-full z-50 bg-slate-50/80 backdrop-blur-xl shadow-[0_2px_12px_rgba(0,0,0,0.06)]">
        <div className="flex justify-between items-center px-8 py-4 max-w-screen-2xl mx-auto md:pl-80">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden text-slate-600 hover:text-blue-700 transition-all active:scale-95"
            >
              <span className="material-symbols-outlined">menu</span>
            </button>
            <span className="text-2xl font-bold text-blue-900 font-headline tracking-tight">
              EducaMundo
            </span>
          </div>
          <div className="flex items-center gap-6">
            <nav className="hidden lg:flex items-center gap-8">
              <Link
                to="/"
                className="text-blue-900 font-bold font-headline tracking-tight"
              >
                Meus Cursos
              </Link>
              <a
                className="text-slate-600 font-medium hover:text-blue-700 transition-colors font-headline tracking-tight"
                href="#"
              >
                Explorar
              </a>
              <a
                className="text-slate-600 font-medium hover:text-blue-700 transition-colors font-headline tracking-tight"
                href="#"
              >
                Certificados
              </a>
            </nav>
            <div className="flex items-center gap-4">
              <button className="text-slate-600 hover:text-blue-700 transition-all active:scale-95">
                <span className="material-symbols-outlined">notifications</span>
              </button>
              <button className="text-slate-600 hover:text-blue-700 transition-all active:scale-95">
                <span className="material-symbols-outlined">account_circle</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="pt-24 pb-12 px-4 md:pl-80 md:pr-8 min-h-screen">
        <div className="max-w-5xl mx-auto space-y-12">
          {/* Lesson Header */}
          <div className="flex flex-col gap-2">
            <div className="flex items-center gap-2 text-secondary font-bold text-xs tracking-widest uppercase">
              <span>Conteúdo</span>
              <span className="w-1 h-1 rounded-full bg-outline-variant inline-block" />
              <span>Aula</span>
            </div>
            <h1 className="text-4xl md:text-5xl font-headline font-extrabold text-primary leading-tight tracking-tight">
              {selectedTopicName || (loading ? 'Carregando...' : 'Selecione uma aula')}
            </h1>
          </div>

          {/* Video + Transcription */}
          <section className="space-y-8">
            <div className="relative group aspect-video w-full bg-primary rounded-xl overflow-hidden shadow-2xl">
              {videoItem ? (
                <iframe
                  className="w-full h-full"
                  src={`https://www.youtube.com/embed/${videoItem.content}`}
                  title="YouTube Video"
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              ) : (
                <div className="flex items-center justify-center h-full">
                  {loading ? (
                    <p className="text-white/60">Carregando vídeo...</p>
                  ) : (
                    <div className="w-20 h-20 bg-secondary text-white rounded-full flex items-center justify-center shadow-xl">
                      <span
                        className="material-symbols-outlined text-4xl"
                        style={{ fontVariationSettings: "'FILL' 1" }}
                      >
                        play_arrow
                      </span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {transcriptionItems.length > 0 && (
              <div className="bg-surface-container-low rounded-xl p-8 space-y-4">
                <div className="flex items-center justify-between">
                  <h3 className="font-headline font-bold text-primary flex items-center gap-2">
                    <span className="material-symbols-outlined">notes</span>
                    Transcrição da Aula
                  </h3>
                </div>
                <div className="text-on-surface-variant leading-relaxed space-y-4">
                  {transcriptionItems.map((item, i) => (
                    <p key={i}>{item.content}</p>
                  ))}
                </div>
              </div>
            )}
          </section>

          {/* Separator */}
          <div className="h-16 flex items-center justify-center">
            <div className="w-16 h-1 rounded-full bg-surface-container-highest" />
          </div>

          {/* Activity Section */}
          {activityData && (
            <section className="bg-white rounded-xl shadow-sm overflow-hidden">
              <div className="p-8 md:p-12 space-y-8">
                <div className="space-y-4">
                  <span className="px-3 py-1 bg-tertiary-fixed text-on-tertiary-fixed font-bold text-xs rounded-full">
                    ATIVIDADE PRÁTICA
                  </span>
                  <h2 className="text-2xl font-headline font-extrabold text-primary">
                    {activityData.question}
                  </h2>
                </div>

                <div className="grid gap-4">
                  {activityData.options?.map((option, i) => (
                    <label
                      key={i}
                      className={`flex items-start gap-4 p-5 rounded-lg cursor-pointer transition-colors ${
                        selectedAnswer === i
                          ? 'bg-secondary-fixed text-on-secondary-fixed ring-2 ring-secondary'
                          : 'bg-surface-container-low hover:bg-surface-container'
                      }`}
                    >
                      <input
                        type="radio"
                        name="activity"
                        className="mt-1 w-5 h-5 text-secondary border-outline focus:ring-secondary shrink-0"
                        checked={selectedAnswer === i}
                        onChange={() => {
                          if (!answerSubmitted) setSelectedAnswer(i);
                        }}
                      />
                      <p
                        className={`leading-tight ${
                          selectedAnswer === i ? 'font-bold' : 'font-medium text-on-surface'
                        }`}
                      >
                        {option.text}
                      </p>
                    </label>
                  ))}
                </div>

                <div className="flex flex-col md:flex-row items-center justify-between gap-6 pt-6 border-t border-outline-variant/10">
                  <div className="flex items-center gap-2 text-on-surface-variant text-sm">
                    <span className="material-symbols-outlined text-tertiary">info</span>
                    <span>Esta resposta vale pontos de experiência.</span>
                  </div>
                  <button
                    onClick={() => setAnswerSubmitted(true)}
                    disabled={selectedAnswer === null || answerSubmitted}
                    className="w-full md:w-auto px-8 py-4 bg-primary text-on-primary font-bold rounded-md hover:shadow-lg transition-all active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Confirmar Resposta
                  </button>
                </div>

                {answerSubmitted && (
                  <div
                    className={`p-4 rounded-lg font-bold ${
                      activityData.options?.[selectedAnswer]?.correct
                        ? 'bg-green-100 text-green-800'
                        : 'bg-error-container text-on-error-container'
                    }`}
                  >
                    {activityData.options?.[selectedAnswer]?.correct
                      ? 'Correto! Parabéns!'
                      : 'Incorreto. Tente novamente!'}
                  </div>
                )}
              </div>
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-slate-100 w-full py-12 md:pl-72">
        <div className="flex flex-col items-center gap-6 px-4">
          <div className="flex flex-wrap justify-center gap-6 text-slate-500 text-xs tracking-wide">
            <a className="hover:text-blue-700 transition-all duration-300" href="#">
              Termos de Uso
            </a>
            <a className="hover:text-blue-700 transition-all duration-300" href="#">
              Privacidade
            </a>
            <a className="hover:text-blue-700 transition-all duration-300" href="#">
              Suporte
            </a>
            <a className="hover:text-blue-700 transition-all duration-300" href="#">
              Trabalhe Conosco
            </a>
          </div>
          <p className="text-slate-500 text-center text-xs tracking-wide">
            © 2024 EducaMundo - Transformando o Futuro através da Educação.
          </p>
        </div>
      </footer>
    </div>
  );
};

export default Content;
