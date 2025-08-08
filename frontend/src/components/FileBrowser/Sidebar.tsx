import { useState } from 'react';
import { FileItem } from './types';

interface SidebarProps {
  currentPath: string;
  onPathChange: (path: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({
  currentPath,
  onPathChange
}) => {
  const [expandedFolders, setExpandedFolders] = useState<Record<string, boolean>>({});
  const [folders, setFolders] = useState<FileItem[]>([
    { id: '1', name: 'Documents', path: '/Documents', type: 'folder', size: 0, modified: new Date().toISOString(), created: new Date().toISOString() },
    { id: '2', name: 'Images', path: '/Images', type: 'folder', size: 0, modified: new Date().toISOString(), created: new Date().toISOString() },
    { id: '3', name: 'Videos', path: '/Videos', type: 'folder', size: 0, modified: new Date().toISOString(), created: new Date().toISOString() },
  ]);

  const toggleFolder = (folderId: string) => {
    setExpandedFolders(prev => ({
      ...prev,
      [folderId]: !prev[folderId]
    }));
  };

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <h3>Folders</h3>
      </div>
      <div className="folder-tree">
        {folders.map(folder => (
          <div key={folder.id} className="folder-item">
            <div
              className={`folder-name ${currentPath === folder.path ? 'active' : ''}`}
              onClick={() => onPathChange(folder.path)}
            >
              <span
                className="folder-toggle"
                onClick={(e) => {
                  e.stopPropagation();
                  toggleFolder(folder.id);
                }}
              >
                {expandedFolders[folder.id] ? '📂' : '📁'}
              </span>
              {folder.name}
            </div>
            {expandedFolders[folder.id] && (
              <div className="subfolders">
                {/* TODO: Fetch and display subfolders */}
              </div>
            )}
          </div>
        ))}
      </div>
      <div className="sidebar-footer">
        <button className="new-folder-btn">+ New Folder</button>
      </div>
    </div>
  );
};

export default Sidebar;
