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
  const [workList, setWorkList] = useState<Work[]>([]);
  const [page, setPage] = useState(1);
  const [nextCursors, setNextCursors] = useState<{ last_date: string | null, last_id: string | null }[]>([
    { last_date: null, last_id: null },
  ]);
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(true);

  const limit = 10;

  const fetchPage = (pageNumber: number) => {
    if (!authorId) return;

    const cursor = nextCursors[pageNumber - 1];
    const totalSent = (pageNumber - 1) * limit;

    let apiUrl = `http://127.0.0.1:8000/api/authors/${authorId}/works/?limit=${limit}&total_sent=${totalSent}`;
    if (cursor?.last_date && cursor?.last_id) {
      apiUrl += `&last_date=${cursor.last_date}&last_id=${cursor.last_id}`;
    }

    setLoading(true);
    fetch(apiUrl)
      .then((res) => {
        if (!res.ok) throw new Error(`Error HTTP: ${res.status}`);
        return res.json();
      })
      .then((data: {
        results: Work[];
        next_last_date: string | null;
        next_last_id: string | null;
        has_more: boolean;
      }) => {
        setWorkList(data.results); // reemplaza si usas paginación de página a página

        setHasMore(data.has_more);

        if (data.next_last_date && data.next_last_id && nextCursors.length === pageNumber) {
          setNextCursors((prev) => [
            ...prev,
            { last_date: data.next_last_date, last_id: data.next_last_id },
          ]);
        }

        setLoading(false);
      })
      .catch((err) => {
        console.error("Error al obtener datos:", err);
        setLoading(false);
      });
  };

  useEffect(() => {
    if (authorId) {
      fetchPage(1);
    }
  }, [authorId]);

  const handleNext = () => {
    if (hasMore) {
      const nextPage = page + 1;
      setPage(nextPage);
      fetchPage(nextPage);
    }
  };

  const handlePrev = () => {
    if (page > 1) {
      const prevPage = page - 1;
      setPage(prevPage);
      fetchPage(prevPage);
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

  if (!workList || workList.length === 0) {
    return <p>No hay trabajos disponibles.</p>;
  }

  return (
    <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6 w-6/10">
      <h3 className="px-4 mb-2 text-xl font-semibold">Trabajos</h3>
      {workList.map((work: Work) => (
        <div
          key={work.id}
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
          disabled={page === 1}
          className={`px-4 py-2 rounded-lg ${
            page === 1
              ? "bg-gray-200 text-gray-500 cursor-not-allowed"
              : "bg-gray-800 text-white hover:bg-gray-700 cursor-pointer"
          }`}
        >
          Anterior
        </button>

        <span className="text-sm font-medium text-gray-600">
          Página {page}
        </span>

        <button
          onClick={handleNext}
          disabled={!hasMore}
          className={`px-4 py-2 rounded-lg ${
            !hasMore
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
