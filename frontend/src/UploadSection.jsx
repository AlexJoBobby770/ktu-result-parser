import { useState } from "react";
import FileInput from "./FileInput";

export default function UploadSection() {
  const [pdfFile, setPdfFile] = useState(null);
  const [masterFile, setMasterFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");

  const canUpload = pdfFile && masterFile;

  const handleUpload = async () => {
    setUploadStatus("Uploading files...");

    const formData = new FormData();
    formData.append("pdf", pdfFile);
    formData.append("master", masterFile);

    try {
      const res = await fetch("http://localhost:8000/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error();

      setUploadStatus("✅ Files uploaded successfully");
    } catch {
      setUploadStatus("❌ Upload failed");
    }
  };

  return (
    <section className="upload-section">
      <h2>Upload Files</h2>
      <p className="section-description">
        Select the KTU result PDF and student master file to begin
        processing.
      </p>

      <div className="upload-form">
        <FileInput
          label="📄 KTU Result PDF"
          requirement="Required • PDF only"
          accept=".pdf"
          file={pdfFile}
          setFile={setPdfFile}
        />

        <FileInput
          label="📊 Student Master File"
          requirement="Required • Excel or CSV"
          accept=".xlsx,.xls,.csv"
          file={masterFile}
          setFile={setMasterFile}
        />

        <button
          className="upload-btn"
          disabled={!canUpload}
          onClick={handleUpload}
        >
          Upload & Process
        </button>

        {uploadStatus && (
          <div className="upload-status">
            {uploadStatus}
          </div>
        )}
      </div>
    </section>
  );
}
