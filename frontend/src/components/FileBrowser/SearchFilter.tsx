import { useState, useEffect } from 'react';
import { FileItem } from './types';

interface SearchFilterProps {
  onSearch: (query: string) => void;
  onFilter: (filters: Record<string, any>) => void;
  currentPath: string;
}

const SearchFilter: React.FC<SearchFilterProps> = ({
  onSearch,
  onFilter,
  currentPath
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    fileType: '',
    minSize: '',
    maxSize: '',
    modifiedAfter: '',
    modifiedBefore: ''
  });
  const [showAdvanced, setShowAdvanced] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => {
      onSearch(searchQuery);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchQuery, onSearch]);

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const applyFilters = () => {
    onFilter(filters);
  };

  const resetFilters = () => {
    setFilters({
      fileType: '',
      minSize: '',
      maxSize: '',
      modifiedAfter: '',
      modifiedBefore: ''
    });
    onFilter({});
  };

  return (
    <div className="search-filter-container">
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search files..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <button
          className="advanced-toggle"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          {showAdvanced ? 'Hide Filters' : 'Show Filters'}
        </button>
      </div>

      {showAdvanced && (
        <div className="advanced-filters">
          <div className="filter-group">
            <label>File Type</label>
            <select
              name="fileType"
              value={filters.fileType}
              onChange={handleFilterChange}
            >
              <option value="">All Types</option>
              <option value="image">Images</option>
              <option value="document">Documents</option>
              <option value="video">Videos</option>
              <option value="audio">Audio</option>
              <option value="archive">Archives</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Size Range (KB)</label>
            <div className="size-range">
              <input
                type="number"
                name="minSize"
                placeholder="Min"
                value={filters.minSize}
                onChange={handleFilterChange}
              />
              <span>to</span>
              <input
                type="number"
                name="maxSize"
                placeholder="Max"
                value={filters.maxSize}
                onChange={handleFilterChange}
              />
            </div>
          </div>

          <div className="filter-group">
            <label>Modified Date</label>
            <div className="date-range">
              <input
                type="date"
                name="modifiedAfter"
                value={filters.modifiedAfter}
                onChange={handleFilterChange}
              />
              <span>to</span>
              <input
                type="date"
                name="modifiedBefore"
                value={filters.modifiedBefore}
                onChange={handleFilterChange}
              />
            </div>
          </div>

          <div className="filter-actions">
            <button onClick={applyFilters}>Apply Filters</button>
            <button className="secondary" onClick={resetFilters}>Reset</button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SearchFilter;
