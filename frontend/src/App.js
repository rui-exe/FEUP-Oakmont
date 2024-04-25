import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import './styles/styles.css';
import Profile from './components/profile';
import SignInPage from './components/signInPage';
import SignUpPage from './components/signUpPage';
import Layout from './components/layout';
import { AuthProvider } from './auth/AuthContext';
import 'tailwindcss/tailwind.css';

const App = () => {
  return (
    <Router>
      <AuthProvider>
        <Layout>
          <Routes>
            <Route path="/users/:username" element={<Profile />} />
            <Route path="/" element={<h1>Home</h1>} />
            <Route path="/sign-in" element={<SignInPage />} />
            <Route path="/sign-up" element={<SignUpPage />} />
          </Routes>
        </Layout>
      </AuthProvider>
    </Router>
  );
}

export default App;