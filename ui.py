import React, { useState } from "react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FileText, UploadCloud } from "lucide-react";
import Papa from "papaparse";

export default function TimeSeriesUpload() {
  const [fileName, setFileName] = useState(null);
  const [fileData, setFileData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith(".csv")) {
      setFileName(file.name);
      Papa.parse(file, {
        header: true,
        skipEmptyLines: true,
        complete: function (results) {
          setFileData(results.data);
        },
      });
    } else {
      alert("Please upload a valid CSV file.");
    }
  };

  const runDetectionPipeline = async () => {
    setLoading(true);
    // Placeholder logic for future backend call
    setTimeout(() => {
      setResults([
        { timestamp: "2025-04-01 10:00", type: "Contextual", confidence: 0.89 },
        { timestamp: "2025-04-02 14:30", type: "Collective", confidence: 0.93 },
      ]);
      setLoading(false);
    }, 2000);
  };

  return (
    <div className="p-4 space-y-6 max-w-2xl mx-auto">
      <Card className="p-4">
        <CardContent className="space-y-4">
          <h2 className="text-xl font-bold">Upload Your Time Series CSV File</h2>
          <Input type="file" accept=".csv" onChange={handleFileChange} />
          {fileName && (
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4" />
              <span>{fileName}</span>
            </div>
          )}
          <Button onClick={runDetectionPipeline} disabled={!fileData || loading}>
            <UploadCloud className="w-4 h-4 mr-2" />
            {loading ? "Processing..." : "Run Anomaly Detection"}
          </Button>
        </CardContent>
      </Card>

      {results && (
        <Card className="p-4">
          <CardContent>
            <h3 className="text-lg font-semibold mb-2">Anomaly Detection Results</h3>
            <ul className="space-y-2">
              {results.map((result, idx) => (
                <li key={idx} className="border rounded p-2">
                  <strong>Time:</strong> {result.timestamp} <br />
                  <strong>Type:</strong> {result.type} <br />
                  <strong>Confidence:</strong> {(result.confidence * 100).toFixed(2)}%
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
