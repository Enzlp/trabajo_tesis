import { useLocation} from "react-router-dom";
import RecommendedCard from "./RecommendedCard";
import FilterCard from "./FilterCard";
import StatsCard from './StatsCard';
import { useEffect, useState } from "react";
import MetricsCard from "./MetricsCard";

// Importar SVG como URL (evita errores de React con SVG complejos)
import InfoCircle from "../../assets/info-circle.svg?url";

interface Concept {
  id: string;
  display_name: string;
}

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

export default function Results() {
	const location = useLocation();
	const [loading, setLoading] = useState<boolean>(true) 
	const [totalResult, setTotalResult] = useState<number>(0)
	const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

	//Definir payload de fetch
	const [conceptList, setConceptList] = useState<Concept[]>([]);
	const [authorId, setAuthorId] = useState<string>("");

	// Pesos modelos
	const [peso1, setPeso1] = useState<number>(0.5);
	const [peso2, setPeso2] = useState<number>(0.5);

	// Estados para mantener los filtros aplicados
	const [currentOrderBy, setCurrentOrderBy] = useState<string>("sim");
	const [currentLimit, setCurrentLimit] = useState<number>(50);
	const [currentCountry, setCurrentCountry] = useState<string>("");

	// Estado para mostrar/ocultar tooltip
	const [showInfo, setShowInfo] = useState(false);
	const [showInfoRec, setShowInfoRec] = useState(false);
	const [showInfoFilter, setShowInfoFilter] = useState(false);

	// Texto del tooltip
	const infoMetrics =
			"Este modelo es una suma ponderada de un modelo Content-Based (CB) y un modelo de Collaborative Filtering (CF). " +
			"La combinación se hace sobre scores normalizados con Min-Max, para ponderar posiciones relativas. Los pesos deben sumar 1.";

	const infoRecommendations = "Las recomendaciones se definen usando un modelo basado en contenido por afinidad temática y/o un modelo de filtrado colaborativo "+
	"sobre las redes de colaboracion del autor ingresado, la elección de modelo se hace en base al input del usuario, pudiendo generarse recomendaciones individuales o un sistema híbrido dependiendo del caso. Los score definen relevancia en base a el maximo score de afinidad obtenido"+
	" usando una normalizacion min-max para cada modelo y el score total es la ponderacion en base a pesos definidos.";

	const infoFilter = "Se pueden definir filtros para ordenar las recomendaciones en base a score de similitud (posicion relativa), n° de citas y n° de trabajos. Tambien se puede "
	+"filtrar las recomendaciones en base al pais objetivo, y definir un limite de resultados a traer hasta 200. Este filtrado y ordenamiento se hace sobre el total de autores a recomendar.";

	useEffect(() => {
		const cList: Concept[] = location.state?.conceptList || [];
		const aId: string = location.state?.authorId || "";

		setConceptList(cList);
		setAuthorId(aId);

		const fetchRecommendations = async () => {
			try {
				const payload: any = {};

				if (cList.length > 0) {
					payload.concept_vector = cList;
				}

				if (aId !== "") {
					payload.author_id = aId;
				}

				const response = await fetch('http://127.0.0.1:8000/api/recommendation/', {
					method: 'POST',
					headers: { 'Content-Type': 'application/json' },
					body: JSON.stringify(payload),
				});

				if (!response.ok) {
					throw new Error(`HTTP error! status: ${response.status}`);
				}

				const data = await response.json();
				setRecommendations(data.recommendations);
				setTotalResult(data.total_recommendations);
				setLoading(false);


			} catch (err) {
				if (err instanceof Error) console.log(err.message);
			}
		};
		
		fetchRecommendations();
	}, [location.state?.conceptList]);

	// Función para aplicar filtros
	const applyFilters = async (by: string, limit: number, country: string) => {
		try {
			setLoading(true);

			setRecommendations([]);

			setCurrentOrderBy(by);
			setCurrentLimit(limit);
			setCurrentCountry(country);

			const payload: any = {};
			
			if (conceptList.length > 0) {
				payload.concept_vector = conceptList;
			}

			if (authorId !== "") {
				payload.author_id = authorId;
			}

			payload.order_by = by;
			payload.limit = limit;
			
			if (country !== "") {
				payload.country_code = country;
			}

			if (conceptList.length > 0 && authorId !== "") {
				payload.alpha = peso1;
				payload.beta = peso2;
			}

			const response = await fetch('http://127.0.0.1:8000/api/recommendation/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			setRecommendations(data.recommendations);
			setTotalResult(data.total_recommendations);
			setLoading(false);

		} catch (err) {
			if (err instanceof Error) console.log(err.message);
			setLoading(false);
		}
	};

	// Funcion para hacer fetch con pesos manteniendo los filtros
	const weightedFetch = async () => {
		try {
			setLoading(true);
			setRecommendations([]);

			const payload: any = {};
			payload.concept_vector = conceptList;
			payload.author_id = authorId;
			payload.alpha = peso1;
			payload.beta = peso2;

			payload.order_by = currentOrderBy;
			payload.limit = currentLimit;
			
			if (currentCountry !== "") {
				payload.country_code = currentCountry;
			}

			const response = await fetch('http://127.0.0.1:8000/api/recommendation/', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify(payload),
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			setRecommendations(data.recommendations);
			setTotalResult(data.total_recommendations);
			setLoading(false);
		} catch (err) {
			if (err instanceof Error) console.log(err.message);
		}
	}

return (
  <div className="min-h-screen px-3 sm:px-6 md:px-8 py-2 flex flex-col m-2 sm:m-4">
  
    <div className="flex flex-col lg:flex-row w-full gap-4">
      {/* Columna izquierda - Recomendaciones */}
      <div className="flex flex-col w-full lg:w-6/10">
        <div className="flex items-center gap-2 relative mb-4">
          <h1 className="text-xl sm:text-2xl font-bold">Investigadores recomendados</h1>
          <div
            onClick={() => setShowInfoRec(!showInfoRec)}
            className="relative cursor-pointer"
          >
            <img 
              src={InfoCircle}
              alt="info"
              className="w-4 h-4 sm:w-5 sm:h-5"
            />

            {showInfoRec && (
              <>
                {/* Overlay para cerrar al hacer click fuera */}
                <div 
                  className="fixed inset-0 z-10"
                  onClick={() => setShowInfoRec(false)}
                />
                <div
                  className="absolute z-20 w-64 sm:w-72 p-3 right-0 sm:left-6 top-6 sm:top-1/2 sm:-translate-y-1/2
                              bg-gray-800 text-white text-xs rounded-lg shadow-lg"
                >
                  {infoRecommendations}
                </div>
              </>
            )}
          </div>
        </div>
        <RecommendedCard recs={recommendations} loading={loading}/>
      </div>
      
      {/* Columna derecha - Filtros y métricas */}
      <div className="flex flex-col w-full lg:w-4/10">
        <div className="flex flex-col">
          <div className="flex items-center gap-2 relative mb-4">
            <h1 className="text-xl sm:text-2xl font-bold">Filtros</h1>
            <div
              onClick={() => setShowInfoFilter(!showInfoFilter)}
              className="relative cursor-pointer"
            >
              <img 
                src={InfoCircle}
                alt="info"
                className="w-4 h-4 sm:w-5 sm:h-5"
              />

              {showInfoFilter && (
                <>
                  <div 
                    className="fixed inset-0 z-10"
                    onClick={() => setShowInfoFilter(false)}
                  />
                  <div
                    className="absolute z-20 w-64 sm:w-72 p-3 right-0 sm:left-6 top-6 sm:top-1/2 sm:-translate-y-1/2
                                bg-gray-800 text-white text-xs rounded-lg shadow-lg"
                  >
                    {infoFilter}
                  </div>
                </>
              )}
            </div>
          </div>
          <FilterCard filterFunction={applyFilters}/>
        </div>
        <div className="flex flex-col sm:flex-row lg:flex-col xl:flex-row gap-4">
          {conceptList.length > 0 && authorId !== "" && (
            <div className="flex flex-col w-full sm:w-6/10 lg:w-full xl:w-6/10">

              {/* Título Metrics + icono con tooltip */}
              <div className="flex items-center gap-2 relative">
                <h1 className="text-xl sm:text-2xl font-bold my-4">Metrics</h1>

                {/* Ícono con click */}
                <div
                  onClick={() => setShowInfo(!showInfo)}
                  className="relative cursor-pointer"
                >
                  <img 
                    src={InfoCircle}
                    alt="info"
                    className="w-4 h-4 sm:w-5 sm:h-5"
                  />

                  {showInfo && (
                    <>
                      <div 
                        className="fixed inset-0 z-10"
                        onClick={() => setShowInfo(false)}
                      />
                      <div
                        className="absolute z-20 w-64 sm:w-72 p-3 right-0 sm:left-6 top-6 sm:top-1/2 sm:-translate-y-1/2
                                   bg-gray-800 text-white text-xs rounded-lg shadow-lg"
                      >
                        {infoMetrics}
                      </div>
                    </>
                  )}
                </div>
              </div>

              <MetricsCard 
                peso1={peso1} 
                peso2={peso2} 
                setPeso1={setPeso1} 
                setPeso2={setPeso2} 
                fetchFunction={weightedFetch}
              />
            </div>
          )}
          <div className="flex flex-col w-full sm:w-4/10 lg:w-full xl:w-4/10">
            <h1 className="text-xl sm:text-2xl font-bold my-4">Stats</h1>
            <StatsCard totalResult={totalResult} />
          </div>
        </div>
      </div>
    </div>
  </div>
)};