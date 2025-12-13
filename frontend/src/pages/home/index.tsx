import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, User } from 'lucide-react';
import AuthorInput from "./AuthorInput";
import ConceptInput from "./ConceptInput";

interface Concept {
  id: number;
  display_name: string;
}

export default function Home() {
  const [selected, setSelected] = useState<Concept[]>([]);
  const [authorVal, setAuthorVal] = useState<string>("");
  const [searchMode, setSearchMode] = useState<'both' | 'concepts' | 'author'>('both');
  
  const navigate = useNavigate();

  const handleSearchModeChange = (mode: 'both' | 'concepts' | 'author') => {
    setSearchMode(mode);
    setSelected([]);
    setAuthorVal("");
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
    fetch(`https://collabrecommender.dcc.uchile.cl/api/authors/${cleanId}/concepts/`)
      .then((res) => res.json())
      .then((data: Concept[]) => {
        const nuevos = data.filter(
          (c) => !selected.some((s) => s.id === c.id)
        );
        setSelected((prev) => [...prev, ...nuevos]);
      })
      .catch((err) => console.error(err));
  };

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
                <ConceptInput 
                  selected={selected}
                  onSelectedChange={setSelected}
                />
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
                <AuthorInput 
                  onChangeValue={setAuthorVal}
                  value={authorVal}
                />
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