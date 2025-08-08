import { useState } from 'react';
import { FileItem } from './types';

interface FileOperationsProps {
  selectedFiles: string[];
  onOperationComplete: () => void;
  currentPath: string;
}

const FileOperations: React.FC<FileOperationsProps> = ({
  selectedFiles,
  onOperationComplete,
  currentPath
}) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [showMoveModal, setShowMoveModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [newName, setNewName] = useState('');
  const [destinationPath, setDestinationPath] = useState('');

  const handleDelete = async () => {
    try {
      await Promise.all(selectedFiles.map(fileId => (
        fetch(`/api/v1/files/${fileId}`, {
          method: 'DELETE'
        })
      ));
      onOperationComplete();
      setShowDeleteModal(false);
    } catch (error) {
      console.error('Error deleting files:', error);
    }
  };

  const handleRename = async () => {
    if (!newName.trim()) return;

    try {
      await fetch(`/api/v1/files/${selectedFiles[0]}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name: newName })
      });
      onOperationComplete();
      setShowRenameModal(false);
      setNewName('');
    } catch (error) {
      console.error('Error renaming file:', error);
    }
  };

  const handleMove = async () => {
    try {
      await Promise.all(selectedFiles.map(fileId => (
        fetch(`/api/v1/files/${fileId}/move`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ destination_path: destinationPath })
        })
      ));
      onOperationComplete();
      setShowMoveModal(false);
      setDestinationPath('');
    } catch (error) {
      console.error('Error moving files:', error);
    }
  };

  return (
    <div className="file-operations">
      <div className="operation-buttons">
        <button
          onClick={() => setShowRenameModal(true)}
          disabled={selectedFiles.length !== 1}
        >
          Rename
        </button>
        <button onClick={() => setShowMoveModal(true)}>
          Move
        </button>
        <button onClick={() => setShowDeleteModal(true)}>
          Delete
        </button>
        <button onClick={() => setShowShareModal(true)}>
          Share
        </button>
      </div>

      {/* Delete Confirmation Modal */}
      {showDeleteModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Delete {selectedFiles.length} item(s)?</h3>
            <p>This action cannot be undone.</p>
            <div className="modal-actions">
              <button onClick={() => setShowDeleteModal(false)}>Cancel</button>
              <button className="danger" onClick={handleDelete}>Delete</button>
            </div>
          </div>
        </div>
      )}

      {/* Rename Modal */}
      {showRenameModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Rename File</h3>
            <input
              type="text"
              value={newName}
              onChange={(e) => setNewName(e.target.value)}
              placeholder="Enter new name"
            />
            <div className="modal-actions">
              <button onClick={() => setShowRenameModal(false)}>Cancel</button>
              <button onClick={handleRename}>Rename</button>
            </div>
          </div>
        </div>
      )}

      {/* Move Modal */}
      {showMoveModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Move {selectedFiles.length} item(s)</h3>
            <input
              type="text"
              value={destinationPath}
              onChange={(e) => setDestinationPath(e.target.value)}
              placeholder="Enter destination path"
            />
            <div className="modal-actions">
              <button onClick={() => setShowMoveModal(false)}>Cancel</button>
              <button onClick={handleMove}>Move</button>
            </div>
          </div>
        </div>
      )}

      {/* Share Modal */}
      {showShareModal && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Share Files</h3>
            <p>Share functionality coming soon</p>
            <div className="modal-actions">
              <button onClick={() => setShowShareModal(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileOperations;
