import { BreadcrumbItem } from './types';

interface BreadcrumbsProps {
  currentPath: string;
  onPathChange: (path: string) => void;
}

const Breadcrumbs: React.FC<BreadcrumbsProps> = ({
  currentPath,
  onPathChange
}) => {
  const pathParts = currentPath.split('/').filter(Boolean);
  const breadcrumbs: BreadcrumbItem[] = [];

  // Build breadcrumb items
  let accumulatedPath = '';
  for (const part of pathParts) {
    accumulatedPath += `/${part}`;
    breadcrumbs.push({
      name: part,
      path: accumulatedPath
    });
  }

  return (
    <div className="breadcrumbs">
      <button
        className="breadcrumb-home"
        onClick={() => onPathChange('/')}
      >
        Home
      </button>
      {breadcrumbs.map((crumb, index) => (
        <span key={crumb.path}>
          <span className="breadcrumb-separator">/</span>
          {index === breadcrumbs.length - 1 ? (
            <span className="breadcrumb-current">{crumb.name}</span>
          ) : (
            <button
              className="breadcrumb-link"
              onClick={() => onPathChange(crumb.path)}
            >
              {crumb.name}
            </button>
          )}
        </span>
      ))}
    </div>
  );
};

export default Breadcrumbs;
