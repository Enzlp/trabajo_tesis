import { useLocation } from "react-router-dom";

interface Concept {
  id: number;
  display_name: string;
}

export default function Results() {
	const location = useLocation();
	const conceptList: Concept[] = location.state?.conceptList || [];
	

	console.log(conceptList)
    return (
      <div>
      </div>
    )
}