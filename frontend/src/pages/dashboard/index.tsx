import Searchbar from "./Searchbar"
import loading_placeholder from '../../assets/loading_data.svg'

export default function Dashboard(){
	return (
		<div className="w-full h-screen flex flex-col items-center">
			<Searchbar />
			<div className="p-8 bg-white rounded-md items-center justify-center w-1/4 flex flex-col">
				<img src={loading_placeholder} className="w-100 h-100"></img>
				<p className="text-sm font-semibold text-gray-400 text-center">Ingresa un investigador en el buscador para poder generar recomendaciones en base a su red de colaboraciones</p>
			</div>
		</div>
	)
}