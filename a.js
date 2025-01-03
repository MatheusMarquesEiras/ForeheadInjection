function createHtmlElement(item) {
    const { type, name } = item;
  
    switch (type) {
      case 'video':
        return `<div className="flex items-center justify-center iframe-container w-full h-[50vh] mb-8">
                  <iframe
                      class="w-6/12 min-h-[40vh]"
                      src="https://www.youtube.com/embed/${name}"
                      title="YouTube Video"
                      allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                      allowfullscreen>
                  </iframe>

                </div>`;
      case 'transcription':
        return `<div className='flex flex-col items-center justify-start w-full'>
                  <p className='text-xl'>
                    ${name}
                  </p>
                  <button
                    onClick={() => setIsExpanded(!isExpanded)}
                    className="mt-4 text-blue-600 hover:underline"
                  >
                    {isExpanded ? 'Mostrar menos' : 'Mostrar mais'}
                  </button>
                </div>`;
      case 'paragraph':
        return `<p class="paragraph">${name}</p>`;
      default:
        return `<span class="default">${name}</span>`;
    }
  }
  
  // Iterar sobre o array e gerar HTML
  const data = [
    { type: 'video', name: 'WhTgKSkZ6nE?start=0' },
    { type: 'transcription', name: 'Introdução' },
    { type: 'paragraph', name: 'Este é um exemplo de parágrafo.' },
    { type: 'unknown', name: 'Elemento desconhecido' },
  ];
  
  const htmlArray = data.map(createHtmlElement);
  const htmlString = htmlArray.join('\n');
  
  // Adiciona ao DOM (exemplo)
  console.log(htmlString);
  