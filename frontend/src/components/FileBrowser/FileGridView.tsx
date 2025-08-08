import { FileItem } from './types';

interface FileGridViewProps {
  files: FileItem[];
  selectedFiles: string[];
  onFileClick: (fileId: string) => void;
}

const FileGridView: React.FC<FileGridViewProps> = ({
  files,
  selectedFiles,
  onFileClick
}) => {
  return (
    <div className="file-grid">
      {files.map(file => (
        <div
          key={file.id}
          className={`file-grid-item ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
          onClick={() => onFileClick(file.id)}
        >
          <div className="file-icon">
            {file.type === 'folder' ? '📁' : getFileIcon(file.name)}
          </div>
          <div className="file-name">{file.name}</div>
          <div className="file-meta">
            <span>{formatFileSize(file.size)}</span>
            <span>{formatDate(file.modified)}</span>
          </div>
        </div>
      ))}
    </div>
  );
};

function getFileIcon(filename: string): string {
  const ext = filename.split('.').pop()?.toLowerCase();
  switch(ext) {
    case 'pdf': return '📄';
    case 'jpg': case 'png': case 'gif': return '🖼️';
    case 'mp4': case 'mov': return '🎬';
    default: return '📄';
  }
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString();
}

export default FileGridView;
