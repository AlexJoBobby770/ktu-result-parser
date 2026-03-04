import "./App.css";
import { useState, useEffect, useRef } from "react";
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { auth } from './firebase';  // ← You'll create this file
import Auth from "./components/Auth";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";
import Features from "./components/Features";
import Footer from "./components/Footer";

function App() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const uploadSectionRef = useRef(null);

  // Listen for Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
      setUser(currentUser);
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const handleLogout = async () => {
    await signOut(auth);
  };

  // Show loading while checking auth
  if (loading) {
    return (
      <div className="app" style={{ 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        minHeight: '100vh' 
      }}>
        <h2 style={{ color: 'white' }}>Loading...</h2>
      </div>
    );
  }

  // Show login if not authenticated
  if (!user) {
    return <Auth onAuthSuccess={(firebaseUser) => setUser(firebaseUser)} />;
  }

  // Show app if authenticated
  return (
    <div className="app">
      <Navbar 
        currentUser={user.displayName || user.email}
        backendStatus="connected"  // ← Remove useBackendStatus for now
        onLogout={handleLogout}
        uploadSectionRef={uploadSectionRef}
      />
      <Hero uploadSectionRef={uploadSectionRef} />
      <UploadSection 
        ref={uploadSectionRef}
        token={null}  // ← No token needed anymore!
        onLogout={handleLogout}
      />
      <Features />
      <Footer />
    </div>
  );
}

export default App;