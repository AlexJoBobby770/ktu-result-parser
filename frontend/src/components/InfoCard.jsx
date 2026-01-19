function InfoCard({ status }) {
  return (
    <section className="info-card">
      <p>
        This application helps you process KTU result PDFs and generate structured Excel reports.
      </p>
      <p>{status}</p>
    </section>
  );
}

export default InfoCard;
