import { useEffect, useState, useRef } from "react";
import { Search, X } from "lucide-react";

interface Concept {
  id: number;
  display_name: string;
}

type ConceptInputProps = {
  selected: Concept[];
  onSelectedChange: (concepts: Concept[]) => void;
};

function ConceptInput({ selected, onSelectedChange }: ConceptInputProps) {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Concept[]>([]);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [isOpen, setIsOpen] = useState(false);
  const [loading, setLoading] = useState(false);

  const itemRefs = useRef<(HTMLButtonElement | null)[]>([]);
  const cacheRef = useRef<Map<string, Concept[]>>(new Map());

  /* Autocomplete con debounce + cache */
  useEffect(() => {
    if (!query) {
      setResults([]);
      setIsOpen(false);
      setLoading(false);
      return;
    }

    // 1️⃣ Cache inmediato (UX instantánea)
    if (cacheRef.current.has(query)) {
      const cached = cacheRef.current.get(query)!;
      const filtered = cached.filter(
        (item) => !selected.some((s) => s.id === item.id)
      );
      setResults(filtered);
      setLoading(false);
      return;
    }

    const controller = new AbortController();
    setLoading(true);

    const timeoutId = setTimeout(() => {
      fetch(
        `https://collabrecommender.dcc.uchile.cl/api/concept/?search=${query}`,
        { signal: controller.signal }
      )
        .then((res) => res.json())
        .then((data: Concept[]) => {
          cacheRef.current.set(query, data); // 2️⃣ cache
          const filtered = data.filter(
            (item) => !selected.some((s) => s.id === item.id)
          );
          setResults(filtered);
          setHighlightedIndex(-1);
        })
        .catch((err) => {
          if (err.name !== "AbortError") console.error(err);
        })
        .finally(() => {
          setLoading(false);
        });
    }, 300);

    return () => {
      controller.abort();
      clearTimeout(timeoutId);
    };
  }, [query, selected]);

  /* Auto-scroll */
  useEffect(() => {
    if (highlightedIndex >= 0 && itemRefs.current[highlightedIndex]) {
      itemRefs.current[highlightedIndex]?.scrollIntoView({
        block: "nearest",
        behavior: "smooth"
      });
    }
  }, [highlightedIndex]);

  const addTag = (concept: Concept) => {
    onSelectedChange([...selected, concept]);
    setQuery("");
    setResults([]);
    setIsOpen(false);
    setHighlightedIndex(-1);
  };

  const removeTag = (id: number) => {
    onSelectedChange(selected.filter((item) => item.id !== id));
  };

  const cleanConcepts = () => {
    onSelectedChange([]);
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!isOpen || results.length === 0) return;

    switch (e.key) {
      case "ArrowDown":
        e.preventDefault();
        setHighlightedIndex((prev) =>
          prev < results.length - 1 ? prev + 1 : prev
        );
        break;

      case "ArrowUp":
        e.preventDefault();
        setHighlightedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;

      case "Enter":
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < results.length) {
          addTag(results[highlightedIndex]);
        }
        break;

      case "Escape":
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  return (
    <div className="w-full">
      <label htmlFor="concepts" className="block mb-2 text-gray-700 text-sm sm:text-base">
        Conceptos de interés
      </label>
      
      <div className="relative">
        <Search className="absolute left-3 top-3 w-5 h-5 text-gray-400 pointer-events-none" />
        <input
          id="concepts"
          type="text"
          value={query}
          onChange={(e) => {
            const val = e.target.value;
            setQuery(val);

            if (val === "") {
              setIsOpen(false);
              setResults([]);
              return;
            }

            setIsOpen(true);
            setLoading(true);
          }}
          onKeyDown={handleKeyDown}
          placeholder="Escribe un concepto..."
          className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent outline-none text-sm sm:text-base"
        />
        
        {isOpen && (
          <div className="absolute top-full z-10 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {loading && (
              <div className="px-4 py-2 text-gray-400 text-sm sm:text-base">
                Buscando conceptos…
              </div>
            )}

            {!loading && results.length === 0 && (
              <div className="px-4 py-2 text-gray-400 text-sm sm:text-base">
                Sin resultados
              </div>
            )}

            {!loading &&
              results.map((concept, index) => (
                <button
                  key={concept.id}
                  ref={(el) => {
                    itemRefs.current[index] = el;
                  }}
                  type="button"
                  onClick={() => addTag(concept)}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`w-full text-left px-4 py-2 transition-colors text-sm sm:text-base ${
                    index === highlightedIndex
                      ? "bg-teal-100"
                      : "hover:bg-teal-50"
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
              onClick={cleanConcepts}
            >
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
  );
}

export default ConceptInput;