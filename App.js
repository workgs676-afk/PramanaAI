import React, { useRef, useState } from "react";

const ACCEPTED_TYPES = [".pdf", ".png", ".jpg", ".jpeg"];

export default function App() {
  const [file, setFile] = useState(null);
  const [report, setReport] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const applyFile = (selectedFile) => {
    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    setReport(null);
    setError("");
  };

  const handleFile = (event) => {
    applyFile(event.target.files?.[0] ?? null);
  };

  const handleDrop = (event) => {
    event.preventDefault();
    setIsDragging(false);
    applyFile(event.dataTransfer.files?.[0] ?? null);
  };

  const evaluate = async () => {
    if (!file) {
      setError("Choose a bid document before running the evaluation.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    setLoading(true);
    setError("");

    try {
      const response = await fetch("http://127.0.0.1:8000/evaluate-bid", {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        throw new Error("Evaluation request failed.");
      }

      const data = await response.json();
      setReport(data);
    } catch (requestError) {
      setReport(null);
      setError("The backend could not be reached. Start FastAPI and try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={styles.page}>
      <div style={styles.shell}>
        <div style={styles.badge}>PRAMANA AI SYSTEM</div>

        <h1 style={styles.title}>Procurement Intelligence Platform</h1>

        <p style={styles.subtitle}>
          Upload a tender or bid document and receive an instant rule-based
          eligibility assessment from the backend.
        </p>

        <div style={styles.panel}>
          <div style={styles.sectionHeader}>
            <div>
              <div style={styles.sectionEyebrow}>Document intake</div>
              <div style={styles.sectionTitle}>Upload a file to evaluate</div>
            </div>

            <button
              type="button"
              style={styles.secondaryButton}
              onClick={() => fileInputRef.current?.click()}
            >
              Browse files
            </button>
          </div>

          <div
            style={{
              ...styles.uploadBox,
              ...(isDragging ? styles.uploadBoxActive : {})
            }}
            onClick={() => fileInputRef.current?.click()}
            onDragOver={(event) => {
              event.preventDefault();
              setIsDragging(true);
            }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              id="fileInput"
              type="file"
              accept={ACCEPTED_TYPES.join(",")}
              onChange={handleFile}
              style={{ display: "none" }}
            />

            <div style={styles.icon}>↑</div>
            <div style={styles.uploadText}>
              {file ? file.name : "Click or drag a document into this area"}
            </div>
            <div style={styles.uploadSub}>
              Supported formats: PDF, PNG, JPG, JPEG
            </div>
          </div>

          <div style={styles.fileMetaRow}>
            <div style={styles.fileMetaLabel}>Selected file</div>
            <div style={styles.fileMetaValue}>
              {file ? `${file.name} (${Math.ceil(file.size / 1024)} KB)` : "None"}
            </div>
          </div>

          {error ? <div style={styles.errorBanner}>{error}</div> : null}

          <button
            type="button"
            onClick={evaluate}
            style={{
              ...styles.primaryButton,
              ...(loading ? styles.primaryButtonDisabled : {})
            }}
            disabled={loading}
          >
            {loading ? "Analyzing document..." : "Run Evaluation"}
          </button>
        </div>

        <div style={styles.resultsGrid}>
          <div style={styles.card}>
            <div style={styles.sectionEyebrow}>Current run</div>
            <div style={styles.cardTitle}>What the app is doing</div>
            <div style={styles.timeline}>
              <div style={styles.timelineItem}>
                <span style={styles.timelineDot} />
                File selected and prepared for upload
              </div>
              <div style={styles.timelineItem}>
                <span style={styles.timelineDot} />
                FastAPI endpoint checks GST, PAN, and ISO evidence
              </div>
              <div style={styles.timelineItem}>
                <span style={styles.timelineDot} />
                Frontend renders the returned status, score, and summary
              </div>
            </div>
          </div>

          <div style={styles.card}>
            <div style={styles.sectionEyebrow}>Evaluation result</div>
            <div style={styles.cardTitle}>Backend response</div>

            {report ? (
              <>
                <div style={styles.metricsRow}>
                  <div style={styles.metric}>
                    <div style={styles.metricLabel}>Status</div>
                    <div
                      style={{
                        ...styles.metricValue,
                        color:
                          report.status === "PASS" ? "#14532d" : "#991b1b"
                      }}
                    >
                      {report.status}
                    </div>
                  </div>

                  <div style={styles.metric}>
                    <div style={styles.metricLabel}>Score</div>
                    <div style={styles.metricValue}>{report.score}</div>
                  </div>
                </div>

                <div style={styles.summaryCard}>
                  <div style={styles.metricLabel}>Summary</div>
                  <div style={styles.summaryText}>{report.summary}</div>
                </div>
              </>
            ) : (
              <div style={styles.placeholder}>
                Run an evaluation to see the backend result here.
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "32px 18px",
    background:
      "radial-gradient(circle at top left, #f5efe3 0%, #efe2c8 38%, #d9c4a3 100%)",
    color: "#1c1917",
    fontFamily: '"Segoe UI", "Trebuchet MS", sans-serif'
  },
  shell: {
    maxWidth: "1100px",
    margin: "0 auto"
  },
  badge: {
    display: "inline-block",
    marginBottom: "20px",
    padding: "8px 14px",
    borderRadius: "999px",
    background: "rgba(120, 53, 15, 0.08)",
    border: "1px solid rgba(120, 53, 15, 0.16)",
    color: "#92400e",
    fontSize: "11px",
    fontWeight: "700",
    letterSpacing: "0.18em"
  },
  title: {
    margin: 0,
    maxWidth: "700px",
    fontSize: "clamp(2.2rem, 4vw, 4.4rem)",
    lineHeight: 1,
    letterSpacing: "-0.04em"
  },
  subtitle: {
    maxWidth: "700px",
    marginTop: "16px",
    marginBottom: "28px",
    color: "#57534e",
    fontSize: "1rem",
    lineHeight: 1.7
  },
  panel: {
    padding: "24px",
    borderRadius: "28px",
    background: "rgba(255, 251, 235, 0.72)",
    border: "1px solid rgba(120, 53, 15, 0.14)",
    boxShadow: "0 22px 70px rgba(120, 53, 15, 0.12)"
  },
  sectionHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    gap: "16px",
    flexWrap: "wrap"
  },
  sectionEyebrow: {
    fontSize: "12px",
    textTransform: "uppercase",
    letterSpacing: "0.12em",
    color: "#a16207",
    marginBottom: "6px"
  },
  sectionTitle: {
    fontSize: "1.35rem",
    fontWeight: "700"
  },
  secondaryButton: {
    padding: "10px 16px",
    borderRadius: "999px",
    border: "1px solid rgba(120, 53, 15, 0.18)",
    background: "#fffaf0",
    color: "#78350f",
    fontWeight: "600",
    cursor: "pointer"
  },
  uploadBox: {
    marginTop: "20px",
    padding: "34px 20px",
    borderRadius: "22px",
    border: "2px dashed rgba(120, 53, 15, 0.28)",
    background:
      "linear-gradient(135deg, rgba(255,255,255,0.85), rgba(255,247,237,0.92))",
    textAlign: "center",
    cursor: "pointer",
    transition: "transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease"
  },
  uploadBoxActive: {
    transform: "translateY(-2px)",
    borderColor: "#b45309",
    boxShadow: "0 18px 40px rgba(180, 83, 9, 0.16)"
  },
  icon: {
    marginBottom: "10px",
    fontSize: "2rem",
    color: "#b45309"
  },
  uploadText: {
    fontSize: "1rem",
    fontWeight: "700"
  },
  uploadSub: {
    marginTop: "8px",
    color: "#78716c",
    fontSize: "0.95rem"
  },
  fileMetaRow: {
    display: "flex",
    justifyContent: "space-between",
    gap: "16px",
    flexWrap: "wrap",
    marginTop: "18px",
    color: "#57534e",
    fontSize: "0.95rem"
  },
  fileMetaLabel: {
    fontWeight: "700"
  },
  fileMetaValue: {
    color: "#44403c"
  },
  errorBanner: {
    marginTop: "16px",
    padding: "12px 14px",
    borderRadius: "14px",
    background: "#fef2f2",
    border: "1px solid #fecaca",
    color: "#991b1b"
  },
  primaryButton: {
    marginTop: "18px",
    width: "100%",
    padding: "14px 18px",
    border: "none",
    borderRadius: "16px",
    background: "linear-gradient(135deg, #b45309, #d97706)",
    color: "#fff",
    fontSize: "1rem",
    fontWeight: "700",
    cursor: "pointer",
    boxShadow: "0 14px 28px rgba(180, 83, 9, 0.25)"
  },
  primaryButtonDisabled: {
    opacity: 0.75,
    cursor: "progress"
  },
  resultsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(280px, 1fr))",
    gap: "18px",
    marginTop: "18px"
  },
  card: {
    padding: "22px",
    borderRadius: "24px",
    background: "rgba(255, 251, 235, 0.82)",
    border: "1px solid rgba(120, 53, 15, 0.12)",
    boxShadow: "0 18px 55px rgba(120, 53, 15, 0.1)"
  },
  cardTitle: {
    fontSize: "1.15rem",
    fontWeight: "700",
    marginBottom: "14px"
  },
  timeline: {
    display: "grid",
    gap: "12px"
  },
  timelineItem: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    color: "#44403c",
    lineHeight: 1.5
  },
  timelineDot: {
    width: "10px",
    height: "10px",
    borderRadius: "999px",
    background: "#d97706",
    flexShrink: 0
  },
  metricsRow: {
    display: "grid",
    gridTemplateColumns: "repeat(2, minmax(0, 1fr))",
    gap: "14px"
  },
  metric: {
    padding: "16px",
    borderRadius: "18px",
    background: "#fffbeb",
    border: "1px solid rgba(120, 53, 15, 0.12)"
  },
  metricLabel: {
    marginBottom: "8px",
    color: "#78716c",
    fontSize: "0.78rem",
    textTransform: "uppercase",
    letterSpacing: "0.08em"
  },
  metricValue: {
    fontSize: "1.8rem",
    fontWeight: "800",
    color: "#1c1917"
  },
  summaryCard: {
    marginTop: "14px",
    padding: "16px",
    borderRadius: "18px",
    background: "#fffaf0",
    border: "1px solid rgba(120, 53, 15, 0.12)"
  },
  summaryText: {
    color: "#44403c",
    lineHeight: 1.7
  },
  placeholder: {
    padding: "20px",
    borderRadius: "18px",
    background: "#fffbeb",
    color: "#78716c",
    lineHeight: 1.7
  }
};
