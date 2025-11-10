import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import AuthorInput from "./AuthorInput";

interface Concept {
  id: number;
  display_name: string;
}


export default function Home() {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Concept[]>([]);
  const [selected, setSelected] = useState<Concept[]>([]);
  const [isActive, setIsActive] = useState(false);
  const [authorVal, setAuthorVal] = useState<string>("")
  const navigate = useNavigate();

  useEffect(() => {
    if (!query) {
      setResults([]);
      return;
    }

    const timeoutId = setTimeout(() => {
      fetch(`http://127.0.0.1:8000/api/concept/?search=${query}`)
        .then((res) => res.json())
        .then((data: Concept[]) => {
          const filtered = data.filter(
            (item) => !selected.some((s) => s.id === item.id)
          );
          setResults(filtered);
        })
        .catch((err) => console.error(err));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query, selected]);

  const addTag = (concept: Concept) => {
    setSelected([...selected, concept]);
    setQuery("");
    setResults([]);
  };

  const removeTag = (id: number) => {
    setSelected(selected.filter((item) => item.id !== id));
  };

  const searchRecommended = () => {
    if (selected.length > 0 || authorVal !== "") {
      navigate("/results", { state: { conceptList: selected, authorId: authorVal } });
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-150">
      <div className="w-1/2">
        {/* Sección fija del header y controles */}
        <div className="text-center">
          <h1 className="text-2xl font-bold mb-2 text-start">
            Busca recomendaciones de interés
          </h1>
          <p className="text-sm font-semibold text-gray-400 mb-4 text-start">
            Busca y selecciona conceptos relacionados con inteligencia artificial
            en la barra de búsqueda. Una vez elegidos, presiona "Recomendar" para
            generar recomendaciones acordes a los conceptos seleccionados.
          </p>

          {/* Search bar */}
          <div className="relative flex">
            <input
              type="text"
              placeholder="Buscar Conceptos..."
              className="flex-1 p-2 border border-gray-300 rounded-l"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button
              className="p-2 bg-[#00d1b2] text-white rounded-r font-semibold cursor-pointer"
              onClick={searchRecommended}
            >
              Recomendar
            </button>

            {/* Dropdown */}
            {results.length > 0 && (
              <ul className="absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b max-h-60 overflow-y-auto z-20 text-start">
                {results.map((item) => (
                  <li
                    key={item.id}
                    className="p-2 cursor-pointer hover:bg-gray-100"
                    onClick={() => addTag(item)}
                  >
                    {item.display_name}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {/* Busqueda por autor */}
          <div className="py-2 flex items-center gap-3 justify-start">
            <span className="text-gray-700 font-semibold text-base">Recomendar por autor</span>
            <button
              onClick={() => setIsActive(!isActive)}
              className={`relative w-12 h-6 rounded-full transition-colors duration-200 cursor-pointer ${
                isActive ? 'bg-teal-500' : 'bg-gray-300'
              }`}
            >
              <span
                className={`absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full transition-transform duration-200 ${
                  isActive ? 'translate-x-6' : 'translate-x-0'
                }`}
              />
            </button>
            {/* Input para busqueda por autor*/}
            {isActive && (
              <AuthorInput value={authorVal} onChangeValue={setAuthorVal}/>
            )}
          </div>
        </div>

        {/* Contenedor de tags con altura mínima para empujar hacia abajo */}
        <div className="mt-4 min-h-[60px]">
          {selected.length > 0 && (
            <div className="flex flex-wrap justify-center gap-2">
              {selected.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center bg-blue-100 text-blue-800 px-3 py-1 rounded-full"
                >
                  <span>{item.display_name}</span>
                  <button
                    className="ml-2 font-bold cursor-pointer"
                    onClick={() => removeTag(item.id)}
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}