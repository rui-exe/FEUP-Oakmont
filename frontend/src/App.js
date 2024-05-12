import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './styles/styles.css';
import Profile from './components/profile';
import SignInPage from './components/signInPage';
import SignUpPage from './components/signUpPage';
import FinancialInstrumentPage from './components/financialInstrumentPage';
import Layout from './components/layout';
import { AuthProvider } from './auth/AuthContext';
import 'tailwindcss/tailwind.css';
import HomePage from './components/homePage';
import PostPage from './components/postPage';

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/users/:username" element={<Profile />} />
            <Route path="/" element={<HomePage />} />
            <Route path="/sign-in" element={<SignInPage />} />
            <Route path="/sign-up" element={<SignUpPage />} />
            <Route path="/items/:symbol" element={<FinancialInstrumentPage />} />
            <Route path="/posts/:username/:post_id" element={<PostPage />} />
            <Route path="*" element={<h1>Not Found</h1>} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
}

export default App;