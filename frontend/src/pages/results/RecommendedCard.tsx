import { useState } from "react";
import LoadingRecommendations from './LoadingRecommendations';
import { useNavigate } from "react-router-dom";
import { User, BookOpen, ExternalLink, Globe, TrendingUp, Award } from "lucide-react";

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
      <div className="bg-white rounded-2xl shadow-md border border-gray-100 p-6 sm:p-8">
        <div className="flex flex-col items-center justify-center text-center">
          <div className="w-14 h-14 sm:w-16 sm:h-16 bg-gray-100 rounded-full flex items-center justify-center mb-3 sm:mb-4">
            <User className="w-7 h-7 sm:w-8 sm:h-8 text-gray-400" />
          </div>
          <h3 className="text-gray-700 text-base sm:text-lg font-semibold mb-2">
            No se encontraron recomendaciones
          </h3>
          <p className="text-gray-500 text-sm">
            Intenta ajustar los filtros o criterios de búsqueda
          </p>
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
    <div className="space-y-4 sm:space-y-6">
      {currentRecs.map((rec: Recommendation, index: number) => (
        <div
          key={rec.author_id}
          className="group bg-white rounded-xl sm:rounded-2xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden border border-gray-100 hover:border-teal-200"
        >
          <div className="p-4 sm:p-5 md:p-6">
            <div className="flex flex-col lg:flex-row gap-4 sm:gap-6">
              {/* Left: Avatar and Rank */}
              <div className="flex lg:flex-col items-center lg:items-start gap-3 sm:gap-4">
                {/* Rank Badge */}
                <div className="flex-shrink-0">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-lg sm:rounded-xl flex items-center justify-center font-semibold text-sm sm:text-base ${
                    startIndex + index === 0 ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white shadow-lg' :
                    startIndex + index === 1 ? 'bg-gradient-to-br from-gray-300 to-gray-400 text-white shadow-lg' :
                    startIndex + index === 2 ? 'bg-gradient-to-br from-orange-400 to-orange-600 text-white shadow-lg' :
                    'bg-gray-100 text-gray-600'
                  }`}>
                    #{startIndex + index + 1}
                  </div>
                </div>
                
                {/* Avatar */}
                <div className="flex-shrink-0">
                  <div className="w-16 h-16 sm:w-20 sm:h-20 bg-gradient-to-br from-teal-100 to-cyan-100 rounded-xl sm:rounded-2xl flex items-center justify-center ring-2 sm:ring-4 ring-white shadow-lg">
                    <User className="w-8 h-8 sm:w-10 sm:h-10 text-teal-600" />
                  </div>
                </div>
              </div>

              {/* Center: Content */}
              <div className="flex-1 min-w-0">
                {/* Name and Institution */}
                <div className="mb-3 sm:mb-4">
                  <div className="flex items-start justify-between gap-3 sm:gap-4 mb-2">
                    <h2 className="text-lg sm:text-xl font-bold text-gray-900 group-hover:text-teal-600 transition-colors break-words">
                      {rec.display_name}
                    </h2>
                    
                    {/* Relevance Score - Desktop */}
                    <div className="hidden sm:flex items-center gap-2 px-3 sm:px-4 py-2 bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl border border-teal-200 flex-shrink-0">
                      <Award className="w-4 h-4 sm:w-5 sm:h-5 text-teal-600" />
                      <div>
                        <div className="text-xs text-gray-600">Relevancia</div>
                        <div className="text-base sm:text-lg font-bold text-teal-700">
                          {(rec.similarity_score * 100).toFixed(2)}%
                        </div>
                      </div>
                    </div>
                  </div>
                  <p className="text-sm sm:text-base text-gray-600 flex items-start sm:items-center gap-2 flex-wrap">
                    <Globe className="w-4 h-4 text-gray-400 flex-shrink-0 mt-0.5 sm:mt-0" />
                    <span className="font-semibold break-words">{rec.institution_name}</span>
                    <span className="hidden sm:inline">—</span>
                    <span className="break-words">{latamCountryCodes[rec.country_code]}</span>
                  </p>
                </div>

                {/* Model Scores */}
                <div className="flex flex-wrap gap-2 sm:gap-3 mb-3 sm:mb-4">
                  <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 sm:py-2 bg-teal-50 rounded-lg border border-teal-100">
                    <div className="w-2 h-2 bg-teal-500 rounded-full flex-shrink-0"></div>
                    <span className="text-xs sm:text-sm text-gray-600">Afinidad temática:</span>
                    <span className="text-xs sm:text-sm font-semibold text-teal-700">
                      {rec.cb_score === 0 ? "-" : `${(rec.cb_score * 100).toFixed(2)}%`}
                    </span>
                  </div>
                  <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1.5 sm:py-2 bg-purple-50 rounded-lg border border-purple-100">
                    <div className="w-2 h-2 bg-purple-500 rounded-full flex-shrink-0"></div>
                    <span className="text-xs sm:text-sm text-gray-600">Red de colaboración:</span>
                    <span className="text-xs sm:text-sm font-semibold text-purple-700">
                      {rec.cf_score === 0 ? "-" : `${(rec.cf_score * 100).toFixed(2)}%`}
                    </span>
                  </div>
                </div>

                {/* Relevance Score - Mobile */}
                <div className="sm:hidden flex items-center gap-2 px-3 py-2 bg-gradient-to-r from-teal-50 to-cyan-50 rounded-xl border border-teal-200 mb-3 w-fit">
                  <Award className="w-4 h-4 text-teal-600" />
                  <div>
                    <div className="text-xs text-gray-600">Relevancia</div>
                    <div className="text-base font-bold text-teal-700">
                      {(rec.similarity_score * 100).toFixed(2)}%
                    </div>
                  </div>
                </div>

                {/* Topics */}
                <div className="mb-3 sm:mb-4">
                  <div className="flex flex-wrap gap-1.5 sm:gap-2">
                    {rec.top_concepts.map((concept: ConceptScore) => (
                      <span
                        key={concept.concept_id}
                        className="px-2.5 sm:px-3 py-1 sm:py-1.5 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg text-xs sm:text-sm transition-colors break-words"
                      >
                        {concept.display_name}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Stats */}
                <div className="flex flex-wrap gap-4 sm:gap-6 mb-3 sm:mb-4 pb-3 sm:pb-4 border-b border-gray-100">
                  <div className="flex items-center gap-2">
                    <div className="w-9 h-9 sm:w-10 sm:h-10 bg-blue-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <BookOpen className="w-4 h-4 sm:w-5 sm:h-5 text-blue-600" />
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Publicaciones</div>
                      <div className="text-gray-900 font-bold text-sm sm:text-base">{rec.works_count}</div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-9 h-9 sm:w-10 sm:h-10 bg-green-50 rounded-lg flex items-center justify-center flex-shrink-0">
                      <TrendingUp className="w-4 h-4 sm:w-5 sm:h-5 text-green-600" />
                    </div>
                    <div>
                      <div className="text-gray-500 text-xs">Citas</div>
                      <div className="text-gray-900 font-bold text-sm sm:text-base">{rec.cited_by_count}</div>
                    </div>
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col sm:flex-row flex-wrap gap-2 sm:gap-3">
                  <button
                    onClick={() => navigate(`/authors/${rec.author_id.split("/").pop()}`)}
                    className="inline-flex items-center justify-center gap-2 px-4 sm:px-5 py-2 sm:py-2.5 bg-gradient-to-r from-teal-500 to-cyan-600 text-white rounded-lg hover:from-teal-600 hover:to-cyan-700 transition-all shadow-md hover:shadow-lg font-medium text-sm sm:text-base"
                  >
                    <User className="w-4 h-4" />
                    <span>Ver perfil completo</span>
                  </button>
                  
                  {rec.orcid && (
                    <a
                      href={rec.orcid}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center justify-center gap-2 px-4 sm:px-5 py-2 sm:py-2.5 border-2 border-gray-300 text-gray-700 rounded-lg hover:border-teal-500 hover:text-teal-600 hover:bg-teal-50 transition-all font-medium text-sm sm:text-base"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Ver ORCID</span>
                    </a>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      ))}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3 sm:gap-4 mt-6 sm:mt-8">
          <button
            onClick={prevPage}
            disabled={page === 1}
            className="px-4 sm:px-5 py-2 sm:py-2.5 bg-white border-2 border-gray-300 text-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-all font-medium text-sm sm:text-base"
          >
            Anterior
          </button>

          <span className="text-xs sm:text-sm text-gray-600">
            Página <span className="font-bold text-teal-600">{page}</span> de{" "}
            <span className="font-bold text-teal-600">{totalPages}</span>
          </span>

          <button
            onClick={nextPage}
            disabled={page === totalPages}
            className="px-4 sm:px-5 py-2 sm:py-2.5 bg-white border-2 border-gray-300 text-gray-700 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-all font-medium text-sm sm:text-base"
          >
            Siguiente
          </button>
        </div>
      )}
    </div>
  );
}