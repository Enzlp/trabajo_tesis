import { useEffect, useState, useRef } from "react";

interface Author {
  author_id: string;
  display_name: string;
}

type AuthorInputProps = {
  onChangeValue: (nuevoValor: string) => void;
};


function AuthorInput({onChangeValue}: AuthorInputProps) {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Author[]>([]);


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
    onChangeValue(author.author_id);
    setQuery(author.display_name);
    setResults([]);                 
  };

  return (
    <div className="flex w-full max-w-sm">
      <div className="flex flex-col flex-1 relative">
        <input
          type="text"
          placeholder="Buscar..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="bg-white border border-gray-300 p-1 rounded-md focus:outline-none w-full"
        />

        {results.length > 0 && (
          <ul className="absolute top-full left-0 w-full bg-white border border-gray-300 rounded-b-md max-h-60 overflow-y-auto z-20 text-start">
            {results.map((item) => (
              <li
                key={item.author_id}
                className="p-2 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSelect(item)}
              >
                {item.display_name}
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}

export default AuthorInput;
