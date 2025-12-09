import { Header } from './components/TitleBar';
import { DashboardControls } from './components/DashboardControls';
import { FactorFocusCard } from './components/FactorFocusCard';

function App() {
  return (
    <div className="min-h-screen bg-[#080b12] text-white">
      <Header />
      
      <main className="max-w-[1800px] mx-auto px-8 md:px-12 lg:px-16 py-10">
        <DashboardControls />
        
        {/* Factor Focus of the Week */}
        <FactorFocusCard />
      </main>
    </div>
  );
}

export default App;
