import { useLocation} from "react-router-dom";
import RecommendedCard from "./RecommendedCard";
import FilterCard from "./FilterCard";
import StatsCard from './StatsCard';
import { useEffect, useState } from "react";
import MetricsCard from "./MetricsCard";

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

			// Limpiamos recomendaciones
			setRecommendations([]);

			// Guardar los filtros aplicados en el estado
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

			// Agregar parámetros de filtro al payload
			payload.order_by = by;
			payload.limit = limit;
			
			if (country !== "") {
				payload.country_code = country;
			}

			// Si existen pesos personalizados, incluirlos
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

			// Limpiamos recomendaciones
			setRecommendations([]);

			const payload: any = {};
			payload.concept_vector = conceptList;
			payload.author_id = authorId;
			payload.alpha = peso1;
			payload.beta = peso2;

			// Mantener los filtros aplicados
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
		<div className="min-h-screen px-8 py-2 flex flex-col m-4">
		
			<div className="flex w-full gap-4">
				<div className="flex flex-col w-6/10">
					<h1 className="text-2xl font-bold mb-4">Investigadores recomendados</h1>
					<RecommendedCard recs={recommendations} loading={loading}/>
				</div>
				
				<div className="flex flex-col w-4/10">
					<div className="flex flex-col">
						<h1 className="text-2xl font-bold mb-4">Filtros</h1>
						<FilterCard filterFunction={applyFilters}/>
					</div>
					<div className="flex gap-4">
						{conceptList.length > 0 && authorId !== "" && (
							<div className="flex flex-col w-6/10">
								<h1 className="text-2xl font-bold my-4">Metrics</h1>
								<MetricsCard peso1={peso1} peso2={peso2} setPeso1={setPeso1} setPeso2={setPeso2} fetchFunction={weightedFetch}/>
							</div>
						)}
						<div className="flex flex-col w-4/10">
							<h1 className="text-2xl font-bold my-4">Stats</h1>
							<StatsCard totalResult={totalResult} />
						</div>
					</div>
				</div>
			</div>
		</div>
	)
}