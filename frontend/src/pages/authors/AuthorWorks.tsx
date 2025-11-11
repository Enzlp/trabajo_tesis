import { useEffect, useState } from "react"
import { useParams } from "react-router-dom";
import loading_animation from "../../assets/loading_animation.svg";

interface Work{
  cited_by_count: number;
  display_name: string;
  doi: string;
  id: string;
  is_paratext: boolean;
  is_retracted: boolean;
  language: string;
  publication_date: string;
  publication_year: number;
  title: string;
  type: string;
}



export default function AuthorWorks() {
  const { authorId } = useParams<{ authorId: string }>();
  const [allWorks, setAllWorks] = useState<Work[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [loading, setLoading] = useState(true);

  const itemsPerPage = 10;

  // Calcular paginación local
  const totalPages = Math.ceil(allWorks.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentWorks = allWorks.slice(startIndex, endIndex);

  // Fetch de todos los works (hasta 100) una sola vez
  useEffect(() => {
    if (!authorId) return;

    setLoading(true);
    fetch(`http://127.0.0.1:8000/api/authors/${authorId}/works/?limit=100`)
      .then((res) => {
        if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
        return res.json();
      })
      .then((data: { results: Work[]; count: number }) => {
        setAllWorks(data.results);
        setLoading(false);
      })
      .catch((err) => {
        console.error("Error al obtener datos:", err);
        setLoading(false);
      });
  }, [authorId]);

  const handleNext = () => {
    if (currentPage < totalPages) {
      setCurrentPage((prev) => prev + 1);
    }
  };

  const handlePrev = () => {
    if (currentPage > 1) {
      setCurrentPage((prev) => prev - 1);
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col rounded-xl p-6 w-6/10 items-center justify-center">
        <img
          src={loading_animation}
          alt="Cargando..."
          className="w-16 h-16 animate-spin"
        />
      </div>
    );
  }

  if (!allWorks || allWorks.length === 0) {
    return (
      <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 w-6/10">
        <p className="text-center text-gray-500">No hay trabajos disponibles.</p>
      </div>
    );
  }

  const obtainId = (url: string) =>{
    const u = new URL(url);
    // El ID va después del último "/"
    const path = u.pathname;                 // "/W123456"
    const id = path.split("/").filter(Boolean).pop() || "";
    return id;
  }

  return (
    <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 w-6/10">
      <h3 className="px-4 mb-2 text-xl font-bold">
        Trabajos
      </h3>
      
      {currentWorks.map((work: Work) => (
        <div
          key={obtainId(work.id)}
          className="p-4 hover:bg-gray-100 hover:cursor-pointer transition-colors duration-300"
          onClick={() => window.open(work.id, "_blank")}
        >
          <h3
            className="text-base font-semibold"
            dangerouslySetInnerHTML={{ __html: work.title }}
          />
          <div>
            <p className="text-sm text-gray-400 font-semibold">
              {work.publication_year}
            </p>
          </div>
          <div className="flex">
            <p className="text-sm font-medium">
              Citado por {work.cited_by_count} - Idioma: {work.language}
            </p>
          </div>
        </div>
      ))}

      <div className="flex justify-center items-center mt-4 gap-4">
        <button
          onClick={handlePrev}
          disabled={currentPage === 1}
          className={`px-4 py-2 rounded-lg ${
            currentPage === 1
              ? "bg-gray-200 text-gray-500 cursor-not-allowed"
              : "bg-gray-800 text-white hover:bg-gray-700 cursor-pointer"
          }`}
        >
          Anterior
        </button>

        <span className="text-sm font-medium text-gray-600">
          Página {currentPage} de {totalPages}
        </span>

        <button
          onClick={handleNext}
          disabled={currentPage >= totalPages}
          className={`px-4 py-2 rounded-lg ${
            currentPage >= totalPages
              ? "bg-gray-200 text-gray-500 cursor-not-allowed"
              : "bg-gray-800 text-white hover:bg-gray-700 cursor-pointer"
          }`}
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}