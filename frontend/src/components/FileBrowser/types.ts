export interface FileItem {
  id: string;
  name: string;
  path: string;
  size: number;
  type: 'file' | 'folder';
  modified: string;
  created: string;
  mimeType?: string;
  thumbnailUrl?: string;
  previewUrl?: string;
}

export interface BreadcrumbItem {
  name: string;
  path: string;
}

export interface UploadProgress {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'completed' | 'error';
  error?: string;
}
