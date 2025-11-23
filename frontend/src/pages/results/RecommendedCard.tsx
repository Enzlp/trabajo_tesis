import { useState } from "react";
import loading_animation from "../../assets/loading_animation.svg";
import { useNavigate } from "react-router-dom";

type ConceptScore = {
  concept_id: string;
  score: number;
  display_name: string;
}

type Recommendation = {
  author_id: string;
  orcid: string | null;
  display_name: string;
  country_code:string;
  institution_name:string;
  similarity_score: number;
  works_count: number;
  cited_by_count: number;
  top_concepts: ConceptScore[];
};

interface RecommendedCardProps {
  recs: Recommendation[] | null; 
  loading: boolean;
}

export default function RecommendedCard({ recs, loading }: RecommendedCardProps) {
  const [page, setPage] = useState<number>(1);
  const itemsPerPage = 10;
  const navigate = useNavigate();

  const latamCountryCodes: { [key: string]: string } = {
    AR: "Argentina",
    BO: "Bolivia",
    BR: "Brazil",
    CL: "Chile",
    CO: "Colombia",
    CR: "Costa Rica",
    CU: "Cuba",
    DO: "Dominican Republic",
    EC: "Ecuador",
    GT: "Guatemala",
    HN: "Honduras",
    MX: "Mexico",
    NI: "Nicaragua",
    PA: "Panama",
    PE: "Peru",
    PR: "Puerto Rico",
    PY: "Paraguay",
    SV: "El Salvador",
    UY: "Uruguay",
    VE: "Venezuela",
  };

  if ((!recs || recs.length === 0) && loading) {
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

  if((!recs || recs.length === 0) && !loading){
    return (
      <div className="flex flex-col border-2 border-gray-300 rounded-xl">
        <div className="flex justify-center items-center min-h-screen">
          <h3 className="text-gray-500 text-lg font-semibold">No se encontraron recomendaciones para los parametros ingresados</h3>
        </div>
      </div>
    );
  }

  // Los resultados ya vienen ordenados y filtrados desde la API
  const recommendations = recs ?? [];

  const totalPages = Math.ceil(recommendations.length / itemsPerPage);
  const nextPage = () => {
    if (page < totalPages) setPage(page + 1);
  };
  const prevPage = () => {
    if (page > 1) setPage(page - 1);
  };

  const startIndex = (page - 1) * itemsPerPage;
  const currentRecs = recommendations.slice(startIndex, startIndex + itemsPerPage);

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
            <span className="font-bold">{rec.institution_name}</span> - {latamCountryCodes[rec.country_code]}
            </p>
          </div>
          <div className="flex justify-between text-gray-500 font-semibold">
            <div className="flex flex-col">
              <p>N° de trabajos: {rec.works_count}</p>
              <p>N° de citas: {rec.cited_by_count}</p>
            </div>
            <div className="flex flex-col">
              <p className="text-end">
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
              <div className="flex gap-2 justify-end"> 
                {rec.top_concepts.map((concept: ConceptScore)=>(
                    <div
                      key={concept.concept_id}
                      className="flex items-center bg-emerald-200 text-emerald-800 px-2 mt-1  rounded-full"
                      
                    >
                      {concept.display_name}
                    </div>
                ))}
              </div>
            </div>
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