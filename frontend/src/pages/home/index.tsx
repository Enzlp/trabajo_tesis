import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

interface Concept {
  id: number;
  display_name: string;
}


export default function Home() {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Concept[]>([]);
  const [selected, setSelected] = useState<Concept[]>([]); // Aca se van agregando los conceptos para el vector de usuario

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
    // Redirecciona a /results pasando la lista como state
    if(selected.length > 0){
        navigate("/results", { state: { conceptList: selected } });
    }
  };

  return (
    <div className="w-full min-h-120 relative">
      {/* Search bar centrado */}
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-1/2 z-10">
        <div className="flex">
          <input
            type="text"
            placeholder="Buscar Conceptos..."
            className="flex-1 p-2 border border-gray-300 rounded-l"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button className="p-2 bg-[#00d1b2] text-white rounded-r font-semibold cursor-pointer" onClick={searchRecommended}>
            Buscar
          </button>
        </div>

        {/* Dropdown */}
        {results.length > 0 && (
          <ul className="absolute top-full left-0 right-0 bg-white border border-gray-300 rounded-b max-h-60 overflow-y-auto z-20">
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

      {/* Tags debajo, fuera del contenedor centrado */}
      {selected.length > 0 && (
        <div className="absolute top-[60%] left-1/2 transform -translate-x-1/2 w-1/2 flex flex-wrap gap-2">
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
  );
}
