import "./App.css";
import { useRef } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Auth from "./components/Auth";
import { useAuth } from "./hooks/useAuth";
import { useBackendStatus } from "./hooks/useBackendStatus";
import Navbar from "./components/Navbar";
import Hero from "./components/Hero";
import UploadSection from "./components/UploadSection";
import Features from "./components/features";
import Footer from "./components/footer";
import HelpFaq from "./pages/HelpFaq";

function MainApp({ token, currentUser, backendStatus, handleLogout }) {
  const uploadSectionRef = useRef(null);

  return (
    <div className="app">
      <Navbar
        currentUser={currentUser}
        backendStatus={backendStatus}
        onLogout={handleLogout}
        uploadSectionRef={uploadSectionRef}
      />
      <Routes>
        <Route path="/" element={
          <>
            <Hero onScrollToUpload={() => uploadSectionRef.current?.scrollIntoView({ behavior: "smooth" })} />
            <UploadSection ref={uploadSectionRef} token={token} onLogout={handleLogout} />
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
  const { isAuthenticated, token, currentUser, handleAuthSuccess, handleLogout } = useAuth();
  const backendStatus = useBackendStatus();

  if (!isAuthenticated) {
    return <Auth onAuthSuccess={handleAuthSuccess} />;
  }

  return (
    <BrowserRouter>
      <MainApp
        token={token}
        currentUser={currentUser}
        backendStatus={backendStatus}
        handleLogout={handleLogout}
      />
    </BrowserRouter>
  );
}

export default App;