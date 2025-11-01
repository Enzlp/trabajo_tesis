import { useLocation, useNavigate } from "react-router-dom";
import arrowLeft from '../../assets/arrow-left.svg'
import RecommendedCard from "./RecommendedCard";
import FilterCard from "./FilterCard";
import StatsCard from './StatsCard';
import { useEffect, useState } from "react";

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
  const [totalResult, setTotalResult] = useState<number>(0)
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);

  useEffect(() => {
    const conceptList: Concept[] = location.state?.conceptList || [];
    const fetchRecommendations = async () => {
      try {
        const response = await fetch('http://127.0.0.1:8000/api/recommendation/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            concept_vector: conceptList
          })
        });
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        setRecommendations(data.recommendations);
        setTotalResult(data.total_recommendations);
       
      } catch (err) {
        if (err instanceof Error) {
          console.log(err.message);
        }
      }
    };
    
    fetchRecommendations();
  }, [location.state?.conceptList]);

  const goBack = () => {
    navigate('/');
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
          <RecommendedCard recs={recommendations} />
        </div>
        
        <div className="flex flex-col w-4/10">
          <div className="flex flex-col">
            <h1 className="text-2xl font-bold mb-4">Filtros</h1>
            <FilterCard />
          </div>
          <div className="flex flex-col">
            <h1 className="text-2xl font-bold my-4">Stats</h1>
            <StatsCard totalResult={totalResult} />
          </div>
        </div>
      </div>
    </div>
  )
}