import React from 'react';
import { ComingSoonOverlay } from '../../../components/ComingSoonOverlay';

export default function GithublabPage() {
  return (
    <div className="py-12">
      <ComingSoonOverlay 
        title="GitHub integration" 
        description="This feature is currently in development. We are actively building the backend data models and AI orchestrators to support this."
      />
    </div>
  );
}
