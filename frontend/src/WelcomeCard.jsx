import SplitText from "./SplitText";

export default function WelcomeCard({ backendStatus }) {
  return (
    <section className="info-card">
      <SplitText
        text="This application helps you process KTU result PDFs and
        generate structured Excel reports."
        className="info-card-text"
      />
      <p id="backend-status">{backendStatus}</p>
    </section>
  );
}
