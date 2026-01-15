export default function FileInput({
  label,
  requirement,
  accept,
  file,
  setFile,
}) {
  return (
    <div className="file-input-group">
      <label className="file-label">
        <span className="label-text">{label}</span>
        <span className="file-requirement">
          {requirement}
        </span>
      </label>

      <input
        type="file"
        accept={accept}
        className="file-input"
        onChange={(e) => setFile(e.target.files[0])}
      />

      <div className="file-name-display">
        {file ? file.name : "No file selected"}
      </div>
    </div>
  );
}
