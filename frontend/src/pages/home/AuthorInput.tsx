import { useEffect, useState, useRef } from "react";
import { User } from 'lucide-react';

interface Author {
  author_id: string;
  display_name: string;
}

type AuthorInputProps = {
  onChangeValue: (nuevoValor: string) => void;
  value?: string;
};

function AuthorInput({ onChangeValue, value }: AuthorInputProps) {
  const [query, setQuery] = useState<string>("");
  const [results, setResults] = useState<Author[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  const isSelecting = useRef(false);
  const dropdownRef = useRef<HTMLUListElement>(null);
  const itemRefs = useRef<(HTMLLIElement | null)[]>([]);

  // Reset query when the external value changes
  useEffect(() => {
    if (value === "") {
      setQuery("");
      setResults([]);
      setHighlightedIndex(-1);
    }
  }, [value]);

  useEffect(() => {
    if (isSelecting.current) {
      isSelecting.current = false;
      return;
    }

    if (!query) {
      setResults([]);
      setHighlightedIndex(-1);
      return;
    }

    const timeoutId = setTimeout(() => {
      fetch(`http://127.0.0.1:8000/api/authorsearch/?search=${query}`)
        .then((res) => res.json())
        .then((data: Author[]) => {
          setResults(data);
          setHighlightedIndex(-1);
        })
        .catch((err) => console.error(err));
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [query]);

  // Auto-scroll inside dropdown
  useEffect(() => {
    if (highlightedIndex >= 0 && itemRefs.current[highlightedIndex]) {
      itemRefs.current[highlightedIndex]?.scrollIntoView({
        block: "nearest",
        behavior: "smooth"
      });
    }
  }, [highlightedIndex]);

  const handleSelect = (author: Author) => {
    isSelecting.current = true;
    onChangeValue(author.author_id);
    setQuery(author.display_name);
    setResults([]);
    setHighlightedIndex(-1);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (results.length === 0) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;

      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev > 0 ? prev - 1 : -1
        );
        break;

      case "Enter":
        e.preventDefault();
        if (highlightedIndex >= 0) {
          handleSelect(results[highlightedIndex]);
        }
        break;

      case "Escape":
        setResults([]);
        setHighlightedIndex(-1);
        break;
    }
  };

  return (
    <div className="w-full relative">
      {/* Icono izquierdo */}
      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />

      {/* Input responsivo */}
      <input
        id="author"
        type="text"
        placeholder="Ej: María García, Juan Pérez..."
        value={query}
        onChange={(e) => {
          const val = e.target.value;
          setQuery(val);

          if (val === "") {
            onChangeValue("");
          }
        }}
        onKeyDown={handleKeyDown}
        className="
          w-full
          pl-10 pr-4 py-3
          text-sm sm:text-base
          border border-gray-300 
          rounded-lg 
          focus:ring-2 focus:ring-teal-500 focus:border-transparent
          outline-none
          transition
        "
      />

      {/* Dropdown responsivo */}
      {results.length > 0 && (
        <ul
          ref={dropdownRef}
          className="
            absolute top-full left-0 w-full
            bg-white 
            border border-gray-300 
            rounded-b-lg
            max-h-64 sm:max-h-72
            overflow-y-auto 
            z-20
            shadow-md
            mt-1
            text-sm sm:text-base
          "
        >
          {results.map((item, index) => (
            <li
              key={item.author_id}
              ref={(el) => (itemRefs.current[index] = el)}
              className={`
                px-3 py-2 cursor-pointer 
                transition-colors
                ${index === highlightedIndex
                  ? "bg-teal-100"
                  : "hover:bg-gray-100"
                }
              `}
              onClick={() => handleSelect(item)}
              onMouseEnter={() => setHighlightedIndex(index)}
            >
              {item.display_name}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default AuthorInput;
