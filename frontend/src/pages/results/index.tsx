import { useLocation, useNavigate } from "react-router-dom";
import arrowLeft from '../../assets/arrow-left.svg'
import RecommendedCard from "./RecommendedCard";
import FilterCard from "./FilterCard";
import StatsCard from './StatsCard';
import { useEffect, useState } from "react";
import MetricsCard from "./MetricsCard";

interface Concept {
  id: string;
  display_name: string;
}

type Recommendation = {
  author_id: string;
  orcid: string | null;
  display_name: string;
  similarity_score: number;
  works_count: number;
  cited_by_count: number;
}

export default function Results() {
	const location = useLocation();
	const navigate = useNavigate();
	const [loading, setLoading] = useState<boolean>(true) 
	const [totalResult, setTotalResult] = useState<number>(0)
	const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
	const [orderBy, setOrderBy] = useState<string>("");

	//Definir payload de fetch
	const [conceptList, setConceptList] = useState<Concept[]>([]);
	const [authorId, setAuthorId] = useState<string>("");

	// Pesos modelos
	const [peso1, setPeso1] = useState<number>(0.5);
	const [peso2, setPeso2] = useState<number>(0.5);

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

	const goBack = () => {
		navigate('/');
	}

	const changeOrder = (by: string)=>{
		setOrderBy(by);
	}

	// Funcion para hacer fetch con pesos
	const weightedFetch = async () => {
		try{

			setRecommendations([]);
			setLoading(true);

			const payload: any = {};
			payload.concept_vector = conceptList;
			payload.author_id = authorId;
			payload.alpha = peso1;
			payload.beta = peso2;


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
		} catch (err){
			if (err instanceof Error) console.log(err.message)
		}
	}

	return (
		<div className="min-h-screen px-8 py-2 flex flex-col m-4">
		<div className="flex items-center cursor-pointer rounded-2xl hover:bg-gray-200 w-fit p-2 my-2" onClick={goBack}>
			<img src={arrowLeft} className="w-6 h-6" alt="Volver" />
			<h1 className="font-semibold text-lg px-2">Atrás</h1>
		</div>
		
		<div className="flex w-full gap-4">
			<div className="flex flex-col w-6/10">
			<h1 className="text-2xl font-bold mb-4">Investigadores recomendados</h1>
			<RecommendedCard recs={recommendations} orderBy={orderBy} loading={loading}/>
			</div>
			
			<div className="flex flex-col w-4/10">
			<div className="flex flex-col">
				<h1 className="text-2xl font-bold mb-4">Filtros</h1>
				<FilterCard orderFunction ={changeOrder}/>
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