import React from 'react';
import { ComingSoonOverlay } from '../../../components/ComingSoonOverlay';

export default function ReportsPage() {
  return (
    <div className="py-12">
      <ComingSoonOverlay 
        title="Automated Reports" 
        description="This feature is currently in development. We are actively building the backend data models and AI orchestrators to support this."
      />
    </div>
  );
}
