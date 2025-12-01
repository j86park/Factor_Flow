import { Header } from './components/header';

function App() {
  return (
    <div className="min-h-screen bg-dark-bg">
      <Header />
      
      {/* Main content area - we will fill this next */}
      <main className="container mx-auto px-4 py-8">
        <p className="text-gray-500 text-center mt-10">
          Dashboard content will go here...
        </p>
      </main>
    </div>
  );
}

export default App;
