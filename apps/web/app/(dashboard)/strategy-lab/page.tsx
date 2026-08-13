import React from 'react';
import { ComingSoonOverlay } from '../../../components/ComingSoonOverlay';

export default function StrategylabPage() {
  return (
    <div className="py-12">
      <ComingSoonOverlay 
        title="Strategy Lab" 
        description="This feature is currently in development. We are actively building the backend data models and AI orchestrators to support this."
      />
    </div>
  );
}
