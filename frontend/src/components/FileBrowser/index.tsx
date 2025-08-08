import { useState, useEffect } from 'react';
import { FileItem } from './types';
import FileGridView from './FileGridView';
import FileListView from './FileListView';
import Breadcrumbs from './Breadcrumbs';
import Sidebar from './Sidebar';
import UploadZone from './UploadZone';

interface FileBrowserProps {
  initialPath?: string;
  viewMode?: 'grid' | 'list';
}

const FileBrowser: React.FC<FileBrowserProps> = ({
  initialPath = '/',
  viewMode = 'grid'
}) => {
  const [currentPath, setCurrentPath] = useState(initialPath);
  const [files, setFiles] = useState<FileItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedView, setSelectedView] = useState<'grid' | 'list'>(viewMode);
  const [selectedFiles, setSelectedFiles] = useState<string[]>([]);

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/v1/files?path=${currentPath}`);
        const data = await response.json();
        setFiles(data.files);
        setLoading(false);
      } catch (err) {
        setError('Failed to load files');
        setLoading(false);
      }
    };

    fetchFiles();
  }, [currentPath]);

  const handleFileClick = (fileId: string) => {
    setSelectedFiles(prev =>
      prev.includes(fileId)
        ? prev.filter(id => id !== fileId)
        : [...prev, fileId]
    );
  };

  const handlePathChange = (newPath: string) => {
    setCurrentPath(newPath);
  };

  return (
    <div className="file-browser-container">
      <div className="toolbar">
        <Breadcrumbs
          currentPath={currentPath}
          onPathChange={handlePathChange}
        />
        <div className="view-toggle">
          <button
            onClick={() => setSelectedView('grid')}
            className={selectedView === 'grid' ? 'active' : ''}
          >
            Grid
          </button>
          <button
            onClick={() => setSelectedView('list')}
            className={selectedView === 'list' ? 'active' : ''}
          >
            List
          </button>
        </div>
      </div>

      <div className="main-content">
        <Sidebar
          currentPath={currentPath}
          onPathChange={handlePathChange}
        />

        <UploadZone onUploadComplete={() => {}}>
          {loading ? (
            <div className="loading-indicator">Loading...</div>
          ) : error ? (
            <div className="error-message">{error}</div>
          ) : selectedView === 'grid' ? (
            <FileGridView
              files={files}
              selectedFiles={selectedFiles}
              onFileClick={handleFileClick}
            />
          ) : (
            <FileListView
              files={files}
              selectedFiles={selectedFiles}
              onFileClick={handleFileClick}
            />
          )}
        </UploadZone>
      </div>
    </div>
  );
};

export default FileBrowser;
