import { useState } from "react";
import loading_animation from "../../assets/loading_animation.svg";
import { useNavigate } from "react-router-dom";

type Recommendation = {
  author_id: string;
  orcid: string | null;
  display_name: string;
  similarity_score: number;
  works_count: number;
  cited_by_count: number;
};

interface RecommendedCardProps {
  recs: Recommendation[] | null; 
  orderBy: string;
}



export default function RecommendedCard({ recs, orderBy }: RecommendedCardProps) {
  const [page, setPage] = useState<number>(1);
  const itemsPerPage = 8;
  const navigate = useNavigate();

  if (!recs || recs.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <img
          src={loading_animation}
          alt="Cargando..."
          className="w-16 h-16 animate-spin"
        />
      </div>
    );
  }

  // Ordenar según orderBy
  let sortedRecs = [...recs]; // hacer copia para no mutar props
  if (orderBy === 'sim') {
    sortedRecs.sort((a, b) => b.similarity_score - a.similarity_score);
  } else if (orderBy === 'cites') {
    sortedRecs.sort((a, b) => b.cited_by_count - a.cited_by_count);
  } else if (orderBy === 'works') {
    sortedRecs.sort((a, b) => b.works_count - a.works_count);
  }

  const totalPages = Math.ceil(sortedRecs.length / itemsPerPage);
  const nextPage = () => {
    if (page < totalPages) setPage(page + 1);
  };
  const prevPage = () => {
    if (page > 1) setPage(page - 1);
  };

  const startIndex = (page - 1) * itemsPerPage;
  const currentRecs = sortedRecs.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="flex flex-col items-end border-2 border-gray-300 rounded-xl p-6 bg-white min-h-screen">
      {currentRecs.map((rec: Recommendation) => (
        <div
          key={rec.author_id}
          className="w-full p-4 mb-4 rounded bg-indigo-50 flex flex-col cursor-pointer"
          onClick={() => navigate(`/authors/${rec.author_id.split("/").pop()}`)}
        >
          <div className="flex justify-between items-center">
            <h3 className="font-bold text-2xl">{rec.display_name}</h3>
            <p className="text-gray-500 font-semibold">
              Score de similitud: {rec.similarity_score.toFixed(2)}
            </p>
          </div>
          <div className="flex justify-between text-gray-500 font-semibold">
            <div className="flex flex-col">
              <p>N° de trabajos: {rec.works_count}</p>
              <p>N° de citas: {rec.cited_by_count}</p>
            </div>
            <p>
              ORCID:{" "}
              {rec.orcid ? (
                <a
                  href={rec.orcid}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-600 underline"
                >
                  {rec.orcid}
                </a>
              ) : (
                "N/A"
              )}
            </p>
          </div>
        </div>
      ))}

      <div className="flex gap-4 mt-4">
        <button
          onClick={prevPage}
          disabled={page === 1}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50 cursor-pointer"
        >
          Anterior
        </button>
        <span className="self-center">
          Página {page} de {totalPages}
        </span>
        <button
          onClick={nextPage}
          disabled={page === totalPages}
          className="px-4 py-2 bg-gray-200 rounded disabled:opacity-50 cursor-pointer"
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}