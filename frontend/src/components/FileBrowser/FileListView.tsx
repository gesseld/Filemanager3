import { FileItem } from './types';

interface FileListViewProps {
  files: FileItem[];
  selectedFiles: string[];
  onFileClick: (fileId: string) => void;
}

const FileListView: React.FC<FileListViewProps> = ({
  files,
  selectedFiles,
  onFileClick
}) => {
  return (
    <div className="file-list">
      <div className="file-list-header">
        <div className="file-list-name">Name</div>
        <div className="file-list-modified">Modified</div>
        <div className="file-list-size">Size</div>
        <div className="file-list-type">Type</div>
      </div>
      {files.map(file => (
        <div
          key={file.id}
          className={`file-list-item ${selectedFiles.includes(file.id) ? 'selected' : ''}`}
          onClick={() => onFileClick(file.id)}
        >
          <div className="file-list-name">
            <span className="file-icon">
              {file.type === 'folder' ? '📁' : getFileIcon(file.name)}
            </span>
            {file.name}
          </div>
          <div className="file-list-modified">
            {formatDate(file.modified)}
          </div>
          <div className="file-list-size">
            {file.type === 'folder' ? '--' : formatFileSize(file.size)}
          </div>
          <div className="file-list-type">
            {file.type === 'folder' ? 'Folder' : getFileType(file.name)}
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

function getFileType(filename: string): string {
  const ext = filename.split('.').pop()?.toUpperCase();
  return ext || 'File';
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString();
}

export default FileListView;
