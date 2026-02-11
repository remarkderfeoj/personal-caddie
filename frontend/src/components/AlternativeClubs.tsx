import { AlternativeClub } from '../types';

interface AlternativeClubsProps {
  clubs: AlternativeClub[] | undefined;
}

export const AlternativeClubs: React.FC<AlternativeClubsProps> = ({ clubs }) => {
  if (!clubs || clubs.length === 0) {
    return null;
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Alternative Clubs</h3>

      <div className="space-y-3">
        {clubs.map((club, idx) => (
          <div key={idx} className="p-4 border border-gray-200 rounded-lg hover:border-golf-green hover:bg-green-50 transition">
            <div className="flex items-start justify-between mb-2">
              <p className="font-bold text-lg text-gray-800 uppercase">{club.club}</p>
              <span className="bg-golf-green text-white px-3 py-1 rounded-full text-sm font-semibold">
                {club.confidence_percent}%
              </span>
            </div>
            <p className="text-gray-700">{club.rationale}</p>
          </div>
        ))}
      </div>
    </div>
  );
};
