import { useEffect, useState } from "react"
import { useParams } from "react-router-dom";
import loading_animation from "../../assets/loading_animation.svg";
import { ExternalLink, ChevronLeft, ChevronRight } from "lucide-react";

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
      <div className="flex flex-col rounded-xl p-6 items-center justify-center">
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

  
	const getWorkTypeColor = (type: string) => {
		if (type.includes('article')) {
		return 'bg-blue-100 text-blue-700';
		} else if (type.includes('proceedings') || type.includes('conference')) {
		return 'bg-purple-100 text-purple-700';
		} else if (type.includes('chapter')) {
		return 'bg-green-100 text-green-700';
		} else if (type.includes('preprint')) {
		return 'bg-orange-100 text-orange-700';
		}
		return 'bg-gray-100 text-gray-700';
	};
	const getPageNumbers = () => {
  const pages = [];

  if (totalPages <= 7) {
    for (let i = 1; i <= totalPages; i++) pages.push(i);
    return pages;
  }

  // Siempre se muestra la primera página
  pages.push(1);

  // Mostrar ... si estamos lejos del inicio
  if (currentPage > 3) pages.push("...");

  // Páginas intermedias
  const start = Math.max(2, currentPage - 1);
  const end = Math.min(totalPages - 1, currentPage + 1);

  for (let i = start; i <= end; i++) pages.push(i);

  // ... si estamos lejos del final
  if (currentPage < totalPages - 2) pages.push("...");

  // Última página
  pages.push(totalPages);

  return pages;
};

const handlePageClick = (page: number) => {
  setCurrentPage(page);
};	

return (
  <div className="border-2 border-gray-300 rounded-xl overflow-hidden">

    {/* Header */}
    <div className="p-6 border-b border-gray-200">
      <h2 className="text-xl mb-1">Publicaciones Recientes</h2>
      <p className="text-gray-600">
        Mostrando {startIndex + 1}-{Math.min(endIndex, allWorks.length)} de {allWorks.length} publicaciones
      </p>
    </div>

    {/* Tabla */}
    <div className="overflow-x-auto">
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
          {currentWorks.map((work: Work) => (
            <tr key={work.id} className="hover:bg-gray-50 transition-colors">

              	{/* Título */}
				<td className="px-6 py-4 w-full">
				<div className="whitespace-normal break-words">
					{work.title || work.display_name}
					{work.is_retracted && (
					<span className="ml-2 inline-block px-2 py-0.5 bg-red-100 text-red-700 rounded text-xs">
						Retractado
					</span>
					)}
				</div>
				</td>

				{/* Año */}
				<td className="px-6 py-4 text-gray-600">
					{work.publication_year}
				</td>

				{/* Tipo */}
				<td className="px-6 py-4">
					<span
					className={`inline-block px-2 py-1 rounded text-sm ${getWorkTypeColor(work.type)}`}
					>
					{work.type}
					</span>
				</td>

				{/* Citas */}
				<td className="px-6 py-4 text-gray-600">
					{work.cited_by_count.toLocaleString()}
				</td>

				{/* Enlaces */}
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
						rel="noopener noreferrer"
						className="text-teal-600 hover:text-teal-700 inline-flex items-center gap-1 text-sm"
						title="Ver DOI"
						>
						DOI <ExternalLink className="w-3 h-3" />
						</a>
					)}

					<a
						href={work.id}
						target="_blank"
						rel="noopener noreferrer"
						className="text-teal-600 hover:text-teal-700 inline-flex items-center gap-1 text-sm"
						title="Ver en OpenAlex"
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
	<div className="px-6 py-4 border-t border-gray-200 flex items-center justify-between">
	<button
		onClick={handlePrev}
		disabled={currentPage === 1}
		className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
	>
		<ChevronLeft className="w-4 h-4" />
		Anterior
	</button>
	
	<div className="flex items-center gap-1 cursor-pointer">
		{getPageNumbers().map((page, index) => (
		typeof page === 'number' ? (
			<button
			key={index}
			onClick={() => handlePageClick(page)}
			className={`w-10 h-10 rounded-lg transition-colors cursor-pointer ${
				currentPage === page
				? 'bg-teal-500 text-white'
				: 'hover:bg-gray-100 text-gray-700'
			}`}
			>
			{page}
			</button>
		) : (
			<span key={index} className="px-2 text-gray-500">
			{page}
			</span>
		)
		))}
	</div>
	
	<button
		onClick={handleNext}
		disabled={currentPage === totalPages}
		className="cursor-pointer inline-flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
	>
		Siguiente
		<ChevronRight className="w-4 h-4" />
	</button>
	</div>
  </div>
)};
