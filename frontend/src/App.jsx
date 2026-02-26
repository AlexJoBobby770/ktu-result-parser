import "./App.css";
import { useRef } from "react";
import Auth from "./components/Auth";
import { useAuth } from "./hooks/useAuth";
import { useBackendStatus } from "./hooks/useBackendStatus";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";
import Features from "./components/features";
import Footer from "./components/footer";

function App() {
  const { isAuthenticated, token, currentUser, handleAuthSuccess, handleLogout } = useAuth();
  const backendStatus = useBackendStatus();
  const uploadSectionRef = useRef(null);

  if (!isAuthenticated) {
    return <Auth onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <div className="app">
      <Navbar
        currentUser={currentUser}
        backendStatus={backendStatus}
        onLogout={handleLogout}
      />
      <Hero uploadSectionRef={uploadSectionRef} />
      <UploadSection
        ref={uploadSectionRef}
        token={token}
        onLogout={handleLogout}
      />
      <Features />
      <Footer />
    </div>
  );
}

export default App;