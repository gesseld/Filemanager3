import { useState, useCallback } from 'react';
import { UploadProgress } from './types';

interface UploadZoneProps {
  onUploadComplete: () => void;
  children: React.ReactNode;
}

const UploadZone: React.FC<UploadZoneProps> = ({
  onUploadComplete,
  children
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<UploadProgress[]>([]);

  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback(async (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragging(false);

    if (e.dataTransfer.files.length > 0) {
      const files = Array.from(e.dataTransfer.files);
      const newUploads: UploadProgress[] = files.map(file => ({
        file,
        progress: 0,
        status: 'pending'
      }));

      setUploadProgress(prev => [...prev, ...newUploads]);

      // Simulate upload progress
      newUploads.forEach((upload, index) => {
        const interval = setInterval(() => {
          setUploadProgress(prev => {
            const updated = [...prev];
            const uploadIndex = updated.findIndex(u => u.file === upload.file);
            if (uploadIndex !== -1) {
              updated[uploadIndex] = {
                ...updated[uploadIndex],
                progress: Math.min(updated[uploadIndex].progress + 10, 100),
                status: updated[uploadIndex].progress < 100 ? 'uploading' : 'completed'
              };
            }
            return updated;
          });

          if (upload.progress >= 100) {
            clearInterval(interval);
            onUploadComplete();
          }
        }, 300);
      });
    }
  }, [onUploadComplete]);

  return (
    <div
      className={`upload-zone ${isDragging ? 'dragging' : ''}`}
      onDragEnter={handleDragEnter}
      onDragOver={(e) => e.preventDefault()}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
    >
      {isDragging && (
        <div className="drop-overlay">
          <div className="drop-message">Drop files to upload</div>
        </div>
      )}

      {children}

      {uploadProgress.length > 0 && (
        <div className="upload-progress-container">
          {uploadProgress.map((upload, index) => (
            <div key={index} className="upload-progress-item">
              <div className="upload-info">
                <span>{upload.file.name}</span>
                <span>{upload.status === 'completed' ? 'Done' : `${upload.progress}%`}</span>
              </div>
              <div className="progress-bar">
                <div
                  className="progress-fill"
                  style={{ width: `${upload.progress}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default UploadZone;
