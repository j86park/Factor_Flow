import { Header } from './components/TitleBar';
import { DashboardControls } from './components/DashboardControls';

function App() {
  return (
    <div className="min-h-screen bg-dark-bg text-white">
      <Header />
      
      <main className="container mx-auto px-4 py-8 mt-12">
        <DashboardControls />
        
        {/* Placeholder for future grid/charts */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
            {/* Empty state for now */}
        </div>
      </main>
    </div>
  );
}

export default App;
