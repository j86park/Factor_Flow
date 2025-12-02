import { Header } from './components/TitleBar';
import { DashboardControls } from './components/DashboardControls';
import { FactorFocusCard } from './components/FactorFocusCard';

function App() {
  return (
    <div className="min-h-screen bg-[#0d1321] text-white">
      <Header />
      
      <main className="max-w-[1800px] mx-auto px-6 py-10">
        <DashboardControls />
        
        {/* Factor Focus of the Week */}
        <div className="mt-10">
          <FactorFocusCard />
        </div>
      </main>
    </div>
  );
}

export default App;
