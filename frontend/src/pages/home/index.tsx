import { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { Search, User, X } from 'lucide-react';
import AuthorInput from "./AuthorInput";

interface Concept {
  id: number;
  display_name: string;
}


export default function Home() {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Concept[]>([]);
  const [selected, setSelected] = useState<Concept[]>([]);
  const [authorVal, setAuthorVal] = useState<string>("")
  const [searchMode, setSearchMode] = useState<'both' | 'concepts' | 'author'>('both');
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);
  
  const navigate = useNavigate();

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const timeoutId = setTimeout(() => {
      fetch(`https://collabrecommender.dcc.uchile.cl/api/concept/?search=${query}`)
        .then((res) => res.json())
        .then((data: Concept[]) => {
          const filtered = data.filter(
            (item) => !selected.some((s) => s.id === item.id)
          );
          setResults(filtered);
          setHighlightedIndex(-1);
        })
        .catch((err) => console.error(err));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, selected]);

  useEffect(() => {
    if (highlightedIndex >= 0 && itemRefs.current[highlightedIndex]) {
      itemRefs.current[highlightedIndex]?.scrollIntoView({
        block: 'nearest',
        behavior: 'smooth'
      });
    }
  }, [highlightedIndex]);

  const addTag = (concept: Concept) => {
    setSelected([...selected, concept]);
    setQuery("");
    setResults([]);
    setHighlightedIndex(-1);
  };

  const removeTag = (id: number) => {
    setSelected(selected.filter((item) => item.id !== id));
  };

  const handleSearchModeChange = (mode: 'both' | 'concepts' | 'author') => {
    setSearchMode(mode);
    setQuery("");
    setResults([]);
    setSelected([]);
    setAuthorVal("");
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (results.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex((prev) => 
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < results.length) {
          addTag(results[highlightedIndex]);
        }
        break;
      case 'Escape':
        setResults([]);
        setHighlightedIndex(-1);
        break;
    }
  };

  const searchRecommended = (e: React.FormEvent) => {
    e.preventDefault();
    if (selected.length > 0 || authorVal !== "") {
      navigate("/results", { state: { conceptList: selected, authorId: authorVal } });
    }
  };

  const loadAuthorConcepts = () => {
    if (!authorVal) return;
    const cleanId = authorVal.includes("openalex.org/")
      ? authorVal.split("openalex.org/")[1]
      : authorVal;
    fetch(`collabrecommender.dcc.uchile.cl/api/authors/${cleanId}/concepts/`)
      .then((res) => res.json())
      .then((data: Concept[]) => {
        const nuevos = data.filter(
          (c) => !selected.some((s) => s.id === c.id)
        );
        setSelected((prev) => [...prev, ...nuevos]);
      })
      .catch((err) => console.error(err));
  };

  const cleanConcepts = () => {
    setSelected([]);
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="flex items-start justify-center p-3 sm:p-4 pt-4 sm:pt-8">
        <div className="w-full max-w-2xl lg:w-1/2">
          <div className="bg-white rounded-xl border-2 border-gray-300 p-4 sm:p-6 mb-4 sm:mb-6">
            <div className="flex flex-col">
              <h1 className="text-xl sm:text-2xl font-bold mb-2 text-center">
                Busca recomendaciones de interés
              </h1>
              <p className="text-sm sm:text-base text-gray-700 text-justify">
                Genera recomendaciones de investigadores con los que colaborar a partir de tus temas de interés en inteligencia artificial, o ingresa tu nombre (o el de un investigador conocido) para recibir sugerencias basadas en la red de colaboración científica en Latinoamérica.
              </p>
            </div>
            <label className="block font-semibold my-3 text-gray-500 text-sm sm:text-base">Buscar por:</label>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <button
                type="button"
                onClick={() => handleSearchModeChange('both')}
                className={`p-3 sm:p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  searchMode === 'both'
                    ? 'border-teal-500 bg-teal-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Search className="w-5 h-5" />
                  <User className="w-5 h-5" />
                </div>
                <div className="font-medium">Ambos</div>
                <div className="text-gray-500 text-xs sm:text-sm">Conceptos y autor</div>
              </button>

              <button
                type="button"
                onClick={() => handleSearchModeChange('concepts')}
                className={`p-3 sm:p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  searchMode === 'concepts'
                    ? 'border-teal-500 bg-teal-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Search className="w-5 h-5" />
                </div>
                <div className="font-medium">Conceptos</div>
                <div className="text-gray-500 text-xs sm:text-sm">Solo temas de interés</div>
              </button>

              <button
                type="button"
                onClick={() => handleSearchModeChange('author')}
                className={`p-3 sm:p-4 rounded-lg border-2 transition-all cursor-pointer ${
                  searchMode === 'author'
                    ? 'border-teal-500 bg-teal-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-center gap-2 mb-2">
                  <User className="w-5 h-5" />
                </div>
                <div className="font-medium">Investigador</div>
                <div className="text-gray-500 text-xs sm:text-sm">Solo nombre de autor</div>
              </button>
            </div>
          </div>
          
          <form onSubmit={searchRecommended} className="bg-white rounded-xl border-2 border-gray-300 p-4 sm:p-8">
            {(searchMode === 'both' || searchMode === 'concepts') && (
              <div className="mb-6">
                <label htmlFor="concepts" className="block mb-2 text-gray-700 text-sm sm:text-base">
                  Conceptos de interés
                </label>
                <div className="relative">
                  <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400" />
                  <input
                    id="concepts"
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    onKeyDown={handleKeyDown}
                    placeholder="Escribe un concepto..."
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none text-sm sm:text-base"
                  />
                  {results.length > 0 && (
                    <div 
                      ref={dropdownRef}
                      className="absolute top-full z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                      {results.map((concept, index) => (
                        <button
                          key={concept.id}
                          ref={(el) => (itemRefs.current[index] = el)}
                          type="button"
                          onClick={() => addTag(concept)}
                          onMouseEnter={() => setHighlightedIndex(index)}
                          className={`w-full text-left px-4 py-2 transition-colors text-sm sm:text-base ${
                            index === highlightedIndex
                              ? 'bg-teal-100'
                              : 'hover:bg-teal-50'
                          }`}
                        >
                          {concept.display_name}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
                
                {selected.length > 0 && (
                  <div className="mt-3">
                    <div className="flex flex-col sm:flex-row sm:justify-between gap-2 text-xs sm:text-sm text-gray-600 mb-2">
                      <span>Conceptos seleccionados ({selected.length}):</span>
                      <button 
                        type="button"
                        className="bg-indigo-400 hover:bg-indigo-600 px-3 sm:px-4 py-1 text-white rounded-lg cursor-pointer disabled:bg-gray-300 text-xs sm:text-sm w-full sm:w-auto" 
                        onClick={cleanConcepts}>
                        Limpiar
                      </button>
                    </div>
                    <div className="flex flex-wrap gap-2">
                      {selected.map((concept) => (
                        <span
                          key={concept.id}
                          className="inline-flex items-center gap-1 px-2 sm:px-3 py-1 sm:py-1.5 bg-teal-50 text-teal-700 rounded-full border border-teal-200 text-xs sm:text-sm"
                        >
                          <span className="break-words">{concept.display_name}</span>
                          <button
                            type="button"
                            onClick={() => removeTag(concept.id)}
                            className="hover:bg-teal-100 rounded-full p-0.5 transition-colors flex-shrink-0"
                            aria-label={`Remover ${concept.display_name}`}
                          >
                            <X className="w-3 h-3 sm:w-4 sm:h-4 cursor-pointer" />
                          </button>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
            
            {searchMode === 'both' && (
              <div className="flex items-center gap-4 mb-6">
                <div className="flex-1 h-px bg-gray-200"></div>
                <span className="text-gray-400 text-sm">y/o</span>
                <div className="flex-1 h-px bg-gray-200"></div>
              </div>
            )}
            
            {(searchMode === 'both' || searchMode === 'author') && (
              <div className="mb-6">
                <label htmlFor="author" className="block mb-2 text-gray-700 text-sm sm:text-base">
                  Nombre del investigador
                </label>
                <AuthorInput onChangeValue={setAuthorVal} />
              </div>
            )}
            
            {searchMode === 'both' && (
              <div className="mb-6">
                <button
                  type="button"    
                  disabled={authorVal === ""}
                  className="bg-indigo-400 hover:bg-indigo-600 px-3 sm:px-4 py-2 text-white rounded-lg cursor-pointer disabled:bg-gray-300 text-sm sm:text-base w-full sm:w-auto"
                  onClick={loadAuthorConcepts}
                >
                  Cargar conceptos del Autor
                </button>
              </div>
            )}

            <button
              type="submit"
              disabled={selected.length === 0 && authorVal === ""}
              className="w-full py-3 px-4 bg-teal-600 hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed text-white rounded-lg transition-colors cursor-pointer text-sm sm:text-base font-medium"
            >
              Recomendar investigadores
            </button>
          </form>
        </div>
      </div>
    </div>
  );
}