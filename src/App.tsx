import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/Layout';
import { Dashboard } from './pages/Dashboard';
import { Oracle } from './pages/Oracle';
import { Architect } from './pages/Architect';

function App() {
  return (
    <BrowserRouter>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/oracle" element={<Oracle />} />
          <Route path="/architect" element={<Architect />} />
        </Routes>
      </Layout>
    </BrowserRouter>
  );
}

export default App;
