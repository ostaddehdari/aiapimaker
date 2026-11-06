import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faCubesStacked } from '@fortawesome/free-solid-svg-icons';

export function Brand({ compact = false }: { compact?: boolean }) {
  return (
    <div className="brand" aria-label="AI API Maker">
      <div className="brand-symbol" aria-hidden="true">
        <FontAwesomeIcon icon={faCubesStacked} />
      </div>
      {!compact && (
        <div className="brand-name">
          <b>AI API Maker</b>
          <small>درگاه هوش مصنوعی</small>
        </div>
      )}
    </div>
  );
}
