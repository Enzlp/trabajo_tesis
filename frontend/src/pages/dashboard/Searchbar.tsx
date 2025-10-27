import { useEffect, useState, useRef } from "react";

interface Author {
  id: string;
  display_name: string;
}

function Searchbar() {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Author[]>([]);
  const [selected, setSelected] = useState<string>("");


  const isSelecting = useRef(false);

  useEffect(() => {
    if (isSelecting.current) {
      isSelecting.current = false;
      return; 
    }

    if (!query) {
      setResults([]);
      return;
    }

    const timeoutId = setTimeout(() => {
      fetch(`http://127.0.0.1:8000/api/authorsearch/?search=${query}`)
        .then((res) => res.json())
        .then((data: Author[]) => setResults(data))
        .catch((err) => console.error(err));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  const handleSelect = (author: Author) => {
    isSelecting.current = true;       
    setSelected(author.id);
    setQuery(author.display_name);
    setResults([]);                 
  };

  return (
    <div className="p-4 flex w-full max-w-lg">
      <div className="flex flex-col flex-1 relative">
        <input
          type="text"
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="bg-white border border-gray-400 p-2 rounded-l-md focus:outline-none w-full"
        />

        {results.length > 0 && (
          <ul className="absolute top-full left-0 w-full bg-white border border-gray-300 rounded-b-md max-h-60 overflow-y-auto z-20 text-start">
            {results.map((item) => (
              <li
                key={item.id}
                className="p-2 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSelect(item)}
              >
                {item.display_name}
              </li>
            ))}
          </ul>
        )}
      </div>

      <button
        className="bg-[#00d1b2] text-white font-semibold p-2 rounded-r-md cursor-pointer hover:bg-[#00b899]"
        onClick={() => console.log("Autor seleccionado:", selected)}
      >
        Buscar
      </button>
    </div>
  );
}

export default Searchbar;
