import { useState } from 'react';
import { Header } from './components/TitleBar';
import { DashboardControls } from './components/DashboardControls';
import { FactorFocusCard } from './components/FactorFocusCard';
import { TopBottomFactors } from './components/TopBottomFactors';
import { DailyFactorSummary } from './components/DailyFactorSummary';

function App() {
  const [selectedTimeFrame, setSelectedTimeFrame] = useState('1D');

  return (
    <div className="min-h-screen bg-[#080b12] text-white">
      <Header />

      <main className="max-w-[1800px] mx-auto px-8 md:px-12 lg:px-16 py-10">
        <DashboardControls
          selectedTimeFrame={selectedTimeFrame}
          onTimeFrameChange={setSelectedTimeFrame}
        />

        {/* Factor Focus of the Week */}
        <FactorFocusCard />

        {/* Top/Bottom Factors */}
        <TopBottomFactors timeFrame={selectedTimeFrame} />

        {/* Daily Factor Summary - AI Analysis */}
        <DailyFactorSummary />
      </main>
    </div>
  );
}

export default App;

