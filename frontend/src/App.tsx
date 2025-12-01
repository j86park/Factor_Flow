import { Header } from './components/TitleBar';
import { DashboardControls } from './components/DashboardControls';

function App() {
  return (
    <div className="min-h-screen bg-[#0a0e14] text-white">
      <Header />
      
      <main className="max-w-[1800px] mx-auto px-6 py-10">
        <DashboardControls />
        
        {/* Placeholder for future grid/charts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-10">
          {/* Empty state for now */}
        </div>
      </main>
    </div>
  );
}

export default App;
