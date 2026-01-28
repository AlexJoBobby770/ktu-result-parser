function UploadSection({
  pdfFile,
  masterFile,
  setPdfFile,
  setMasterFile,
  onUpload,
  uploadStatus
}) {
  const isEnabled = pdfFile && masterFile;

  return (
    <section className="upload-section">
      <h2>Upload Files Here</h2>

      <div className="file-input-group">
        <label>KTU Result PDF</label>
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setPdfFile(e.target.files[0])}
        />
        <div>{pdfFile ? pdfFile.name : "No file selected"}</div>
      </div>

      <div className="file-input-group">
        <label>Student Master File</label>
        <input
          type="file"
          accept=".xlsx,.xls,.csv"
          onChange={(e) => setMasterFile(e.target.files[0])}
        />
        <div>{masterFile ? masterFile.name : "No file selected"}</div>
      </div>

      <button disabled={!isEnabled} onClick={onUpload}>
        Upload and Process
      </button>

      <div>{uploadStatus}</div>
    </section>
  );
}

export default UploadSection;
