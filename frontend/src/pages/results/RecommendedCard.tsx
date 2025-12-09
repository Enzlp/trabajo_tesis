import { useState } from "react";
import loading_animation from "../../assets/loading_animation.svg";
import { useNavigate } from "react-router-dom";
import { User, BookOpen, ExternalLink} from 'lucide-react';

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
  cb_score: number;
  cf_score: number;
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
        className="w-full p-6 mb-4 rounded-xl bg-white border border-gray-200 shadow-sm hover:shadow-md transition-all"
      >
        <div className="flex flex-col md:flex-row md:items-start gap-6">
          
          {/* Avatar */}
          <div className="flex-shrink-0">
            <div className="w-20 h-20 bg-teal-100 rounded-full flex items-center justify-center">
              <User className="w-10 h-10 text-teal-500" />
            </div>
          </div>

          {/* CONTENIDO DERECHA */}
          <div className="flex-1">
            
            {/* Header: nombre / institución — relevancia */}
            <div className="flex flex-col md:flex-row md:justify-between gap-4 items-start mb-4">

              {/* Nombre + institución */}
              <div >
                <h3 className="font-bold text-xl">{rec.display_name}</h3>
                <p className="text-gray-600 font-semibold text-sm xl:text-base">
                  <span className="font-bold">{rec.institution_name}</span> — {latamCountryCodes[rec.country_code]}
                </p>
              </div>

              {/* Score relativo en la esquina */}
              <div className="flex items-center px-4 py-2 bg-teal-50 rounded-lg border border-teal-200">
                <div>
                  <div className="text-sm text-gray-600">Score Relativo</div>
                  <div className="text-teal-600 text-sm">
                    {(rec.similarity_score * 100).toFixed(2)}%
                  </div>
                </div>
              </div>
            </div>
            
            <div className="flex flex-wrap gap-6 mb-2 text-sm xl:text-base text-gray-600">
              <p>Score modelo CB: {rec.cb_score === 0 ? "-" : `${(rec.cb_score*100).toFixed(2)}%`}</p>
              <p>Score modelo CF: {rec.cf_score === 0 ? "-" : `${(rec.cf_score*100).toFixed(2)}%`}</p>
            </div>

            {/* Conceptos */}
            <div className="flex flex-wrap gap-2 mb-2">
              {rec.top_concepts.map((concept: ConceptScore) => (
                <div
                  key={concept.concept_id}
                  className="flex items-center bg-emerald-200 text-emerald-800 px-3 py-1 rounded-full text-sm"
                >
                  {concept.display_name}
                </div>
              ))}
            </div>

            {/* Stats */}
            <div className="flex flex-wrap gap-6 mb-2 text-gray-600 font-semibold">
              <p className="flex items-center gap-2 text-sm xl:text-base">
                <BookOpen className="w-5 h-5" />
                {rec.works_count} publicaciones
              </p>

              <p className="flex items-center gap-2 text-sm xl:text-base">
                <ExternalLink className="w-5 h-5" />
                {rec.cited_by_count} citas
              </p>
            </div>

            {/* Botones */}
            <div className="flex flex-wrap gap-3 text-sm">
              {rec.orcid && (
                <a
                  href={rec.orcid}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-2 px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition-colors"
                >
                  <ExternalLink className="w-4 h-4" />
                  Ver ORCID
                </a>
              )}

              <button
                className="inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors bg-white cursor-pointer"
                onClick={() =>
                  navigate(`/authors/${rec.author_id.split("/").pop()}`)
                }
              >
                <ExternalLink className="w-4 h-4" />
                Ver perfil completo
              </button>
            </div>
          </div>
        </div>
      </div>
    ))}

    {/* Pagination */}
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
)};
