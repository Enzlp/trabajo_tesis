interface StatsCardProps {
  totalResult: number;
}

export default function StatsCard({ totalResult }: StatsCardProps) {
  return (
    <div className="w-full flex flex-col items-start border-2 border-gray-300 rounded-xl p-4 sm:p-6 bg-white">
      <h3 className="text-lg sm:text-xl md:text-2xl font-semibold">{totalResult} resultados</h3>
    </div>
  )
}