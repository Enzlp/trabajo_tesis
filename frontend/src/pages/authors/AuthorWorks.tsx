import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import loading_animation from "../../assets/loading_animation.svg";
import { ExternalLink, ChevronLeft, ChevronRight } from "lucide-react";

interface Work {
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

  // Fetch inicial
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

  const getWorkTypeColor = (type: string) => {
    if (type.includes("article")) return "bg-blue-100 text-blue-700";
    if (type.includes("proceedings") || type.includes("conference"))
      return "bg-purple-100 text-purple-700";
    if (type.includes("chapter")) return "bg-green-100 text-green-700";
    if (type.includes("preprint")) return "bg-orange-100 text-orange-700";
    return "bg-gray-100 text-gray-700";
  };

  const getPageNumbers = () => {
    const pages = [];
    if (totalPages <= 7) {
      for (let i = 1; i <= totalPages; i++) pages.push(i);
      return pages;
    }
    pages.push(1);
    if (currentPage > 3) pages.push("...");
    const start = Math.max(2, currentPage - 1);
    const end = Math.min(totalPages - 1, currentPage + 1);
    for (let i = start; i <= end; i++) pages.push(i);
    if (currentPage < totalPages - 2) pages.push("...");
    pages.push(totalPages);
    return pages;
  };

  const handlePageClick = (page: number) => setCurrentPage(page);
  const handleNext = () =>
    currentPage < totalPages && setCurrentPage((p) => p + 1);
  const handlePrev = () =>
    currentPage > 1 && setCurrentPage((p) => p - 1);

  // Loading
  if (loading) {
    return (
      <div className="flex flex-col rounded-xl p-6 items-center justify-center">
        <img
          src={loading_animation}
          alt="Cargando..."
          className="w-16 h-16 animate-spin"
        />
      </div>
    );
  }

  // Sin datos
  if (!allWorks.length) {
    return (
      <div className="flex flex-col border-2 border-gray-300 rounded-xl p-6">
        <p className="text-center text-gray-500">No hay trabajos disponibles.</p>
      </div>
    );
  }

  return (
    <div className="border-2 border-gray-300 rounded-xl overflow-hidden">

      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl mb-1">Publicaciones Recientes</h2>
        <p className="text-gray-600 text-sm sm:text-base">
          Mostrando {startIndex + 1}-{Math.min(endIndex, allWorks.length)} de{" "}
          {allWorks.length} publicaciones
        </p>
      </div>

      {/* RESPONSIVO: Cards en móvil / tabla en pantallas grandes */}
      <div className="block lg:hidden p-4 space-y-4">
        {currentWorks.map((work) => (
          <div
            key={work.id}
            className="border rounded-lg p-4 bg-white shadow-sm"
          >
            <h3 className="font-semibold text-base mb-1 break-words">
              {work.title || work.display_name}
            </h3>

            {work.is_retracted && (
              <span className="inline-block px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs mb-2">
                Retractado
              </span>
            )}

            <p className="text-sm text-gray-600">
              <strong>Año:</strong> {work.publication_year || "N/A"}
            </p>

            <p className="text-sm mt-1">
              <span
                className={`inline-block px-2 py-1 rounded text-xs ${getWorkTypeColor(
                  work.type
                )}`}
              >
                {work.type}
              </span>
            </p>

            <p className="text-sm text-gray-700 mt-2">
              <strong>Citas:</strong> {work.cited_by_count.toLocaleString()}
            </p>

            <div className="mt-3 flex flex-col gap-1">
              {work.doi && (
                <a
                  href={
                    work.doi.startsWith("http")
                      ? work.doi
                      : `https://doi.org/${work.doi}`
                  }
                  target="_blank"
                  className="text-teal-600 hover:text-teal-700 text-sm inline-flex items-center gap-1"
                >
                  DOI <ExternalLink className="w-3 h-3" />
                </a>
              )}

              <a
                href={work.id}
                target="_blank"
                className="text-teal-600 hover:text-teal-700 text-sm inline-flex items-center gap-1"
              >
                OpenAlex <ExternalLink className="w-3 h-3" />
              </a>
            </div>
          </div>
        ))}
      </div>

      {/* Tabla completa solo en pantallas ≥ lg */}
      <div className="hidden lg:block overflow-x-auto">
        <table className="w-full border-collapse">
          <thead className="bg-gray-50 border-b border-gray-200">
            <tr>
              <th className="px-6 py-3 text-left text-gray-700">Título</th>
              <th className="px-6 py-3 text-left text-gray-700">Año</th>
              <th className="px-6 py-3 text-left text-gray-700">Tipo</th>
              <th className="px-6 py-3 text-left text-gray-700">Citas</th>
              <th className="px-6 py-3 text-left text-gray-700">Enlaces</th>
            </tr>
          </thead>

          <tbody className="divide-y divide-gray-200">
            {currentWorks.map((work) => (
              <tr key={work.id} className="hover:bg-gray-50 transition-colors">
                <td className="px-6 py-4 w-full break-words">
                  {work.title || work.display_name}
                  {work.is_retracted && (
                    <span className="ml-2 px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
                      Retractado
                    </span>
                  )}
                </td>

                <td className="px-6 py-4">{work.publication_year}</td>

                <td className="px-6 py-4">
                  <span
                    className={`px-2 py-1 rounded text-sm ${getWorkTypeColor(
                      work.type
                    )}`}
                  >
                    {work.type}
                  </span>
                </td>

                <td className="px-6 py-4">
                  {work.cited_by_count.toLocaleString()}
                </td>

                <td className="px-6 py-4">
                  <div className="flex flex-col gap-1">
                    {work.doi && (
                      <a
                        href={
                          work.doi.startsWith("http")
                            ? work.doi
                            : `https://doi.org/${work.doi}`
                        }
                        target="_blank"
                        className="text-teal-600 hover:text-teal-700 text-sm inline-flex items-center gap-1"
                      >
                        DOI <ExternalLink className="w-3 h-3" />
                      </a>
                    )}

                    <a
                      href={work.id}
                      target="_blank"
                      className="text-teal-600 hover:text-teal-700 text-sm inline-flex items-center gap-1"
                    >
                      OpenAlex <ExternalLink className="w-3 h-3" />
                    </a>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className="px-4 py-3 border-t border-gray-200 flex items-center justify-between gap-2">
        {/* Prev */}
        <button
          onClick={handlePrev}
          disabled={currentPage === 1}
          className="inline-flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
        >
          <ChevronLeft className="w-4 h-4" />
          <span className="hidden sm:inline">Anterior</span>
        </button>

        {/* Middle: compact on mobile, full page buttons on sm+ */}
        <div className="flex-1 flex justify-center">
          {/* Mobile compact: show "Página X de Y" */}
          <div className="flex items-center gap-2 sm:hidden text-xs text-gray-600">
            <span>Página</span>
            <span className="font-semibold">{currentPage}</span>
            <span>de</span>
            <span className="font-semibold">{totalPages}</span>
          </div>

          {/* Desktop/tablet: full numbered pagination */}
          <div className="hidden sm:flex items-center gap-2">
            <div className="flex items-center gap-1 overflow-x-auto no-scrollbar px-1">
              {getPageNumbers().map((page, i) =>
                typeof page === "number" ? (
                  <button
                    key={i}
                    onClick={() => handlePageClick(page)}
                    className={`w-9 h-9 sm:w-10 sm:h-10 rounded-lg text-sm flex items-center justify-center transition-colors ${
                      currentPage === page
                        ? "bg-teal-500 text-white"
                        : "hover:bg-gray-100 text-gray-700"
                    }`}
                  >
                    {page}
                  </button>
                ) : (
                  <span key={i} className="px-2 text-gray-500">
                    ...
                  </span>
                )
              )}
            </div>
          </div>
        </div>

        {/* Next */}
        <button
          onClick={handleNext}
          disabled={currentPage === totalPages}
          className="inline-flex items-center gap-2 px-3 py-1.5 sm:px-4 sm:py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-xs sm:text-sm"
        >
          <span className="hidden sm:inline">Siguiente</span>
          <ChevronRight className="w-4 h-4" />
        </button>
      </div>

    </div>
  );
}
