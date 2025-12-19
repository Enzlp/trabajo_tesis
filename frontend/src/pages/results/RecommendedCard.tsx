import { useState } from "react";
import LoadingRecommendations from './LoadingRecommendations';
import { useNavigate } from "react-router-dom";
import { User, BookOpen, ExternalLink } from "lucide-react";

type ConceptScore = {
  concept_id: string;
  score: number;
  display_name: string;
};

type Recommendation = {
  author_id: string;
  orcid: string | null;
  display_name: string;
  country_code: string;
  institution_name: string;
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
    return <LoadingRecommendations />;
  }

  if ((!recs || recs.length === 0) && !loading) {
    return (
      <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6">
        <div className="flex justify-center items-center">
          <h3 className="text-gray-500 text-lg font-semibold">
            No se encontraron recomendaciones para los parámetros ingresados
          </h3>
        </div>
      </div>
    );
  }

  const recommendations = recs ?? [];
  const totalPages = Math.ceil(recommendations.length / itemsPerPage);
  const nextPage = () => page < totalPages && setPage(page + 1);
  const prevPage = () => page > 1 && setPage(page - 1);

  const startIndex = (page - 1) * itemsPerPage;
  const currentRecs = recommendations.slice(startIndex, startIndex + itemsPerPage);

  return (
    <div className="flex flex-col items-end border-2 border-gray-300 rounded-xl p-3 sm:p-4 md:p-6 bg-white">
      {currentRecs.map((rec: Recommendation) => (
        <div
          key={rec.author_id}
          className="w-full p-4 sm:p-6 mb-3 sm:mb-4 rounded-xl bg-white border border-gray-200 shadow-sm hover:shadow-md transition-all"
        >
          <div className="flex flex-col md:flex-row md:items-start gap-4 sm:gap-6">
            {/* Avatar */}
            <div className="flex-shrink-0 mx-auto md:mx-0">
              <div className="w-16 h-16 sm:w-20 sm:h-20 bg-teal-100 rounded-full flex items-center justify-center">
                <User className="w-8 h-8 sm:w-10 sm:h-10 text-teal-500" />
              </div>
            </div>

            {/* CONTENIDO DERECHA */}
            <div className="flex-1">
              {/* Header (nombre, institución + score alineado derecha en md+) */}
              <div className="flex flex-col md:flex-row md:items-start md:justify-between gap-3 sm:gap-4 mb-3 sm:mb-4 w-full">
                {/* Nombre + institución */}
                <div>
                  <h3 className="font-bold text-lg sm:text-xl">{rec.display_name}</h3>
                  <p className="text-gray-600 font-semibold text-xs sm:text-sm">
                    <span className="font-bold">{rec.institution_name}</span> –{" "}
                    {latamCountryCodes[rec.country_code]}
                  </p>
                </div>

                {/* Score relativo */}
                <div className="flex items-center px-3 sm:px-4 py-1.5 sm:py-2 bg-teal-50 rounded-lg border border-teal-200 w-full md:w-auto">
                  <div>
                    <div className="text-xs sm:text-sm text-gray-600">Relevancia total</div>
                    <div className="text-teal-600 text-sm sm:text-base font-semibold">
                      {(rec.similarity_score * 100).toFixed(2)}%
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex flex-wrap gap-3 sm:gap-6 mb-2 text-xs sm:text-sm text-gray-600">
                <p>Afinidad temática (CB): {rec.cb_score === 0 ? "-" : `${(rec.cb_score * 100).toFixed(2)}%`}</p>
                <p>Red de colaboración (CF): {rec.cf_score === 0 ? "-" : `${(rec.cf_score * 100).toFixed(2)}%`}</p>
              </div>

              {/* Conceptos */}
              <div className="flex flex-wrap gap-1.5 sm:gap-2 mb-2">
                {rec.top_concepts.map((concept: ConceptScore) => (
                  <div
                    key={concept.concept_id}
                    className="flex items-center bg-emerald-200 text-emerald-800 px-2 sm:px-3 py-0.5 sm:py-1 rounded-full text-xs sm:text-sm"
                  >
                    {concept.display_name}
                  </div>
                ))}
              </div>

              {/* Stats */}
              <div className="flex flex-wrap gap-3 sm:gap-6 mb-3 text-gray-600 font-semibold">
                <p className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm">
                  <BookOpen className="w-4 h-4 sm:w-5 sm:h-5" />
                  {rec.works_count} publicaciones
                </p>
                <p className="flex items-center gap-1.5 sm:gap-2 text-xs sm:text-sm">
                  <ExternalLink className="w-4 h-4 sm:w-5 sm:h-5" />
                  {rec.cited_by_count} citas
                </p>
              </div>

              {/* Botones */}
              <div className="flex flex-col sm:flex-row flex-wrap gap-2 sm:gap-3 text-xs sm:text-sm">
                {rec.orcid && (
                  <a
                    href={rec.orcid}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center justify-center gap-2 px-3 sm:px-4 py-2 bg-teal-500 text-white rounded-lg hover:bg-teal-600 transition-colors"
                  >
                    <ExternalLink className="w-3 h-3 sm:w-4 sm:h-4" />
                    Ver ORCID
                  </a>
                )}

                <button
                  className="inline-flex items-center justify-center gap-2 px-3 sm:px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors bg-white cursor-pointer"
                  onClick={() => navigate(`/authors/${rec.author_id.split("/").pop()}`)}
                >
                  <ExternalLink className="w-3 h-3 sm:w-4 sm:h-4" />
                  Ver perfil completo
                </button>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Pagination */}
      <div className="flex gap-2 sm:gap-4 mt-4 w-full justify-center sm:justify-end">
        <button
          onClick={prevPage}
          disabled={page === 1}
          className="px-3 sm:px-4 py-1.5 sm:py-2 bg-gray-200 rounded disabled:opacity-50 cursor-pointer text-xs sm:text-sm"
        >
          Anterior
        </button>

        <span className="self-center text-xs sm:text-sm">
          Página {page} de {totalPages}
        </span>

        <button
          onClick={nextPage}
          disabled={page === totalPages}
          className="px-3 sm:px-4 py-1.5 sm:py-2 bg-gray-200 rounded disabled:opacity-50 cursor-pointer text-xs sm:text-sm"
        >
          Siguiente
        </button>
      </div>
    </div>
  );
}
