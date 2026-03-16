import "./App.css";
import { useRef, useState, useEffect } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './firebase';
import Auth from "./components/Auth";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";
import Features from "./components/Features";
import Footer from "./components/Footer";
import HelpFaq from "./pages/HelpFaq";

function MainApp({ user, handleLogout }) {
  const uploadSectionRef = useRef(null);

  return (
    <div className="app">
      <Navbar
        currentUser={user?.displayName || user?.email?.split('@')[0] || 'User'}
        backendStatus="connected"
        onLogout={handleLogout}
        uploadSectionRef={uploadSectionRef}
      />
      <Routes>
        <Route path="/" element={
          <>
            <Hero onScrollToUpload={() => uploadSectionRef.current?.scrollIntoView({ behavior: "smooth" })} />
            <UploadSection ref={uploadSectionRef} onLogout={handleLogout} />
            <Features />
          </>
        } />
        <Route path="/help" element={<HelpFaq />} />
      </Routes>
      <Footer />
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });
    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    try {
      await signOut(auth);
      setUser(null);
    } catch (error) {
      console.error("Logout error:", error);
    }
  };

  if (loading) {
    return (
      <div style={{
        minHeight: '100vh', display: 'flex', alignItems: 'center',
        justifyContent: 'center', background: '#080a0f', color: '#fff'
      }}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
          <div style={{
            width: '40px', height: '40px',
            border: '3px solid rgba(59,130,246,0.2)',
            borderTopColor: '#3b82f6', borderRadius: '50%',
            animation: 'spin 0.8s linear infinite'
          }} />
          <p style={{ fontSize: '0.875rem', color: 'rgba(255,255,255,0.4)' }}>Loading...</p>
        </div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (!user) {
    return <Auth onAuthSuccess={(user) => setUser(user)} />;
  }

  // BrowserRouter wraps MainApp so Navbar can use useNavigate/useLocation
  return (
    <BrowserRouter>
      <MainApp user={user} handleLogout={handleLogout} />
    </BrowserRouter>
  );
}

export default App;