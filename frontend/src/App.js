import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './styles/styles.css';
import Profile from './components/profile';
import Layout from './components/layout';
import 'tailwindcss/tailwind.css';

const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/users/:username" element={<Profile />} />
          <Route path="/" element={<h1>Home</h1>} />
        </Routes>
      </Layout>
    </Router>
  );
}

export default App;